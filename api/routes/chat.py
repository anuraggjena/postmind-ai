import re
import base64
from fastapi import APIRouter, Request, HTTPException
from email.mime.text import MIMEText

from services.gmail_service import (
    get_gmail_service,
    get_header,
    extract_body,
)
from services.ai_service import interpret_intent, generate_reply, summarize_email
from routes.emails import get_emails

router = APIRouter()


# ---------------------------------------------------
# Threaded Gmail Reply
# ---------------------------------------------------
def send_reply(service, to, subject, body, thread_id, message_id):
    msg = MIMEText(body)
    msg["to"] = to
    msg["subject"] = subject
    msg["In-Reply-To"] = message_id
    msg["References"] = message_id

    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    service.users().messages().send(
        userId="me",
        body={
            "raw": raw,
            "threadId": thread_id,
        },
    ).execute()


# ---------------------------------------------------
# Helpers
# ---------------------------------------------------
def extract_email_address(sender):
    match = re.search(r"<(.+?)>", sender)
    return match.group(1) if match else sender


def find_email(request: Request, text: str):
    emails = request.session.get("last_emails", [])
    if not emails:
        return None

    text = text.lower()

    if "that" in text or "this" in text:
        return request.session.get("last_selected_email")

    if "latest" in text or "last" in text:
        return emails[0]

    num = re.search(r"\d+", text)
    if num:
        idx = int(num.group()) - 1
        if 0 <= idx < len(emails):
            return emails[idx]

    if "from" in text:
        sender_key = text.split("from")[-1].strip()
        for e in emails:
            if sender_key in e["from"].lower():
                return e

    for e in emails:
        if any(word in e["subject"].lower() for word in text.split()):
            return e

    return None


# ---------------------------------------------------
# Chat Endpoint
# ---------------------------------------------------
@router.post("/api/chat")
async def chat(request: Request):

    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    service = get_gmail_service(user)

    body = await request.json()
    msg = body.get("message", "").strip().lower()

    # =================================================
    # 1️⃣ CONFIRMATION HANDLER (ALWAYS FIRST)
    # =================================================
    pending = request.session.get("pending_action")

    if pending:
        if msg in ["yes", "y", "confirm", "ok"]:

            if pending["type"] == "delete":
                service.users().messages().trash(
                    userId="me",
                    id=pending["email_id"]
                ).execute()

                request.session.pop("pending_action")

                return {
                    "type": "text",
                    "data": "🗑️ Email deleted successfully."
                }

            if pending["type"] == "reply":
                send_reply(
                    service,
                    pending["to"],
                    pending["subject"],
                    pending["reply"],
                    pending["thread_id"],
                    pending["message_id"],
                )

                request.session.pop("pending_action")

                return {
                    "type": "text",
                    "data": "✅ Reply sent successfully."
                }

        else:
            request.session.pop("pending_action")
            return {
                "type": "text",
                "data": "❌ Action cancelled."
            }

    # =================================================
    # 2️⃣ BASIC COMMANDS
    # =================================================
    if msg in ["hi", "hello", "hey", "good morning", "good evening"]:
        return {
            "type": "text",
            "data": f"Hey {user['name']} 👋 How can I help you with your emails today?"
        }

    if "help" in msg or "what can you do" in msg:
        return {
            "type": "text",
            "data": """Here’s what I can do:

• Show your latest emails  
• Show unread emails (Primary inbox only)  
• Reply to an email  
• Delete emails  
• Summarize emails  

Just tell me what you'd like to do."""
        }

    # =================================================
    # 3️⃣ SHOW EMAILS
    # =================================================
    if "show" in msg or "unread" in msg:

        if "unread" in msg:
            data = await get_emails(request, unread=True)
        else:
            data = await get_emails(request)

        emails = data["emails"]

        request.session["last_emails"] = emails

        return {
            "type": "emails",
            "data": emails
        }

    # =================================================
    # 4️⃣ FETCH EMAILS (only if needed below)
    # =================================================
    data = await get_emails(request)
    emails = data["emails"]
    request.session["last_emails"] = emails

    # =================================================
    # 5️⃣ SUMMARIZE
    # =================================================
    if "summarize" in msg:
        email = find_email(request, msg)
        if not email:
            return {"type": "text", "data": "Email not found."}

        msg_data = service.users().messages().get(
            userId="me",
            id=email["id"]
        ).execute()

        content = extract_body(msg_data["payload"])
        summary = summarize_email(content)

        return {
            "type": "text",
            "data": f"Summary of '{email['subject']}':\n\n{summary}"
        }

    # =================================================
    # 6️⃣ DELETE FLOW
    # =================================================
    if "delete" in msg:
        email = find_email(request, msg)
        if not email:
            return {"type": "text", "data": "Email not found."}

        request.session["last_selected_email"] = email

        request.session["pending_action"] = {
            "type": "delete",
            "email_id": email["id"],
        }

        return {
            "type": "text",
            "data": f"""You are about to delete:

From: {email['from']}
Subject: {email['subject']}

Type YES to confirm."""
        }

    # =================================================
    # 7️⃣ REPLY FLOW
    # =================================================
    if "reply" in msg:
        email = find_email(request, msg)
        if not email:
            return {"type": "text", "data": "Email not found."}

        msg_data = service.users().messages().get(
            userId="me",
            id=email["id"],
        ).execute()

        thread_id = msg_data["threadId"]
        message_id = get_header(
            msg_data["payload"]["headers"],
            "Message-ID"
        )

        content = extract_body(msg_data["payload"])
        to_email = extract_email_address(email["from"])
        reply_text = generate_reply(content, user["name"])

        request.session["last_selected_email"] = email

        request.session["pending_action"] = {
            "type": "reply",
            "to": to_email,
            "subject": f"Re: {email['subject']}",
            "reply": reply_text,
            "thread_id": thread_id,
            "message_id": message_id,
        }

        return {
            "type": "reply_preview",
            "data": {
                "original_subject": email["subject"],
                "reply": reply_text,
            },
        }

    # =================================================
    # 8️⃣ AI INTENT FALLBACK
    # =================================================
    intent = interpret_intent(msg)

    if intent == "show_emails":
        return {
            "type": "emails",
            "data": emails
        }

    if intent == "greeting":
        return {
            "type": "text",
            "data": f"Hi {user['name']} 👋 How can I help you today?"
        }

    if intent == "help":
        return {
            "type": "text",
            "data": "You can ask me to show, reply, delete, or summarize emails."
        }

    return {
        "type": "text",
        "data": "I’m not sure what you meant. Try 'show emails' or 'reply to email 1'."
    }
