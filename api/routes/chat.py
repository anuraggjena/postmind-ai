import os
import re
import base64
from fastapi import APIRouter, Request
from email.mime.text import MIMEText

from services.gmail_service import (
    get_gmail_service,
    get_header,
    extract_body,
)
from services.ai_service import generate_reply
from routes.emails import get_emails

router = APIRouter()


# REAL Gmail reply (threaded)
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


def find_email(emails, text):
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


@router.post("/api/chat")
async def chat(request: Request):
    user = request.session.get("user")
    service = get_gmail_service(user)

    body = await request.json()
    msg = body.get("message", "").lower()

    pending = request.session.get("pending_action")

    # CONFIRMATION HANDLER
    if pending:
        if msg in ["yes", "confirm", "ok", "send", "delete"]:

            if pending["type"] == "delete":
                service.users().messages().trash(
                    userId="me", id=pending["email_id"]
                ).execute()

                request.session.pop("pending_action")
                return {"type": "text", "data": "Email deleted successfully."}

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
                return {"type": "text", "data": "Reply sent successfully."}

        else:
            request.session.pop("pending_action")
            return {"type": "text", "data": "Action cancelled."}

    # FETCH EMAILS
    data = await get_emails(request)
    emails = data["emails"]

    # SHOW EMAILS
    if "show" in msg:
        return {"type": "emails", "data": emails}

    # DELETE FLOW
    if "delete" in msg:
        email = find_email(emails, msg)
        if not email:
            return {"type": "text", "data": "Email not found."}

        request.session["pending_action"] = {
            "type": "delete",
            "email_id": email["id"],
        }

        return {
            "type": "text",
            "data": f"""You are about to delete:

From: {email['from']}
Subject: {email['subject']}

Type YES to confirm.""",
        }

    # REPLY FLOW
    if "reply" in msg:
        email = find_email(emails, msg)
        if not email:
            return {"type": "text", "data": "Email not found."}

        msg_data = service.users().messages().get(
            userId="me", id=email["id"]
        ).execute()

        thread_id = msg_data["threadId"]
        message_id = get_header(
            msg_data["payload"]["headers"], "Message-ID"
        )

        content = extract_body(msg_data["payload"])
        reply_text = generate_reply(content, user["name"])

        request.session["pending_action"] = {
            "type": "reply",
            "to": email["from"],
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

    return {"type": "text", "data": "Command not understood."}
