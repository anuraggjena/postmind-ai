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


# -------------------------
# Proper Gmail Threaded Reply
# -------------------------
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


# -------------------------
# Helper: Find Email
# -------------------------
def find_email(request, text):
    emails = request.session.get("last_emails", [])

    if not emails:
        return None

    if "that" in text or "this" in text:
        # use last referenced email
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

def extract_email_address(sender):
    match = re.search(r"<(.+?)>", sender)
    return match.group(1) if match else sender


# -------------------------
# Chat Endpoint
# -------------------------
@router.post("/api/chat")
async def chat(request: Request):

    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    service = get_gmail_service(user)

    body = await request.json()
    msg = body.get("message", "").strip().lower()

    # -------------------------
    # Basic Greetings
    # -------------------------
    if msg in ["hi", "hii", "hello", "hey", "good morning", "good evening"]:
        return {
            "type": "text",
            "data": f"Hey {user['name']} 👋 How can I help you with your emails today?"
        }

    # -------------------------
    # Help
    # -------------------------
    if "help" in msg or "what can you do" in msg:
        return {
            "type": "text",
            "data": """Here’s what I can help you with:

            • Show your latest emails  
            • Reply to any email  
            • Delete emails by number, sender, or subject  
            • Summarize emails  

            Just tell me what you'd like to do."""
        }

    # -------------------------
    # Confirmation Handling
    # -------------------------
    pending = request.session.get("pending_action")

    if pending:
        if msg in ["yes", "confirm", "ok", "send", "delete"]:

            # DELETE CONFIRM
            if pending["type"] == "delete":
                service.users().messages().trash(
                    userId="me",
                    id=pending["email_id"]
                ).execute()

                request.session.pop("pending_action")

                updated = await get_emails(request)
                request.session["last_emails"] = updated["emails"]

                return {
                    "type": "emails",
                    "data": updated["emails"]
                }

            # REPLY CONFIRM
            if pending["type"] == "reply":

                if msg.startswith("edit"):
                    new_reply = generate_reply(msg, user["name"])
                    pending["reply"] = new_reply
                    request.session["pending_action"] = pending

                    return {
                        "type": "reply_preview",
                        "data": {
                            "original_subject": pending["subject"],
                            "reply": new_reply,
                        },
                    }
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
                "data": "Action cancelled."
            }

    # -------------------------
    # Fetch Emails Only When Needed
    # -------------------------
    data = await get_emails(request)
    emails = data["emails"]

    # store latest list in session
    request.session["last_emails"] = emails

    # -------------------------
    # Show Emails
    # -------------------------
    if "show" in msg:
        return {"type": "emails", "data": emails}
    
    if "unread" in msg:
        data = await get_emails(request, unread=True)
        return {"type": "emails", "data": data["emails"]}

    # --- SUMMARIZE FLOW ---
    if "summarize" in msg:
        email = find_email(emails, msg)

        if not email:
            return {"type": "text", "data": "Email not found."}

        msg_data = service.users().messages().get(
            userId="me",
            id=email["id"],
        ).execute()

        content = extract_body(msg_data["payload"])
        summary = summarize_email(content)

        return {
            "type": "text",
            "data": f"Summary of '{email['subject']}':\n\n{summary}",
        }

    # -------------------------
    # Delete Flow
    # -------------------------
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

    # -------------------------
    # Reply Flow
    # -------------------------
    if "reply" in msg:
        email = find_email(request, msg)
        if not email:
            return {"type": "text", "data": "Email not found."}

        # Fetch full message (for body + metadata)
        msg_data = service.users().messages().get(
            userId="me",
            id=email["id"],
        ).execute()

        thread_id = msg_data["threadId"]
        message_id = get_header(
            msg_data["payload"]["headers"],
            "Message-ID"
        )

        request.session["last_selected_email"] = email

        content = extract_body(msg_data["payload"])
        to_email = extract_email_address(email["from"])
        reply_text = generate_reply(content, user["name"])

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
    
    # --------------------------
    # Summarize
    # --------------------------
    if "summarize" in msg:
        email = find_email(request, msg)
        if not email:
            return {"type": "text", "data": "Email not found."}

        return {
            "type": "text",
            "data": f"Summary:\n\n{email['summary']}"
        }

    # -------------------------
    # AI Intent Fallback
    # -------------------------
    intent = interpret_intent(msg)

    if intent == "show_emails":
        return {"type": "emails", "data": emails}

    if intent == "reply":
        email = find_email(request, msg)
        if email:
            # trigger reply flow
            msg = f"reply {emails.index(email)+1}"

    if intent == "greeting":
        return {
            "type": "text",
            "data": f"Hi {user['name']} 👋 How can I help you today?"
        }

    if intent == "help":
        return {
            "type": "text",
            "data": "You can ask me to show, reply, or delete emails."
        }

    return {
        "type": "text",
        "data": "I'm not sure what you meant. Try saying 'show emails' or 'reply to email 1'."
    }