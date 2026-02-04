import os
import re
import base64
from fastapi import APIRouter, Request
from email.mime.text import MIMEText

from services.gmail_service import (
    get_gmail_service,
    get_header,
    extract_body,
    build_email_map,
)
from services.ai_service import generate_reply
from routes.emails import get_emails

router = APIRouter()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


def send_email(service, to, subject, body):
    msg = MIMEText(body)
    msg["to"] = to
    msg["subject"] = subject
    raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
    service.users().messages().send(userId="me", body={"raw": raw}).execute()


def find_email(emails, text):
    # by number
    num = re.search(r"\d+", text)
    if num:
        idx = int(num.group()) - 1
        if 0 <= idx < len(emails):
            return emails[idx]

    # by sender
    if "from" in text:
        sender_key = text.split("from")[-1].strip()
        for e in emails:
            if sender_key in e["from"].lower():
                return e

    # by subject keyword
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

    # ---------- CONFIRMATION HANDLER ----------
    if pending:
        if msg in ["yes", "confirm", "ok", "send", "delete"]:
            if pending["type"] == "delete":
                service.users().messages().trash(
                    userId="me", id=pending["email_id"]
                ).execute()
                request.session.pop("pending_action")
                return {"type": "text", "data": "Email deleted successfully."}

            if pending["type"] == "reply":
                send_email(
                    service,
                    pending["to"],
                    pending["subject"],
                    pending["reply"],
                )
                request.session.pop("pending_action")
                return {"type": "text", "data": "Reply sent successfully."}

        else:
            request.session.pop("pending_action")
            return {"type": "text", "data": "Action cancelled."}

    # ---------- FETCH EMAILS ----------
    data = await get_emails(request)
    emails = data["emails"]

    # ---------- SHOW ----------
    if "show" in msg:
        return {"type": "emails", "data": emails}

    if "from" in msg:
        sender = msg.split("from")[-1].strip()
        # find latest email from sender

    if "subject" in msg:
        keyword = msg.split("subject")[-1].strip()

    # ---------- DELETE FLOW ----------
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

    # ---------- REPLY FLOW ----------
    if "reply" in msg:
        email = find_email(emails, msg)
        if not email:
            return {"type": "text", "data": "Email not found."}

        msg_data = service.users().messages().get(
            userId="me", id=email["id"]
        ).execute()

        content = extract_body(msg_data["payload"])
        reply_text = generate_reply(content, user["name"])

        request.session["pending_action"] = {
            "type": "reply",
            "email_id": email["id"],
            "to": email["from"],
            "subject": f"Re: {email['subject']}",
            "reply": reply_text,
        }

        return {
            "type": "reply_preview",
            "data": {
                "original_subject": email["subject"],
                "reply": reply_text,
            },
        }

    return {"type": "text", "data": "Command not understood."}
