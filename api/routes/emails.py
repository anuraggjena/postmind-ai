import os
from fastapi import APIRouter, Request
from services.gmail_service import (
    get_gmail_service,
    get_header,
    extract_body,
)
from services.ai_service import summarize_email

router = APIRouter()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")


@router.get("/api/emails")
async def get_emails(request: Request, unread: bool = False):
    user = request.session.get("user")
    service = get_gmail_service(user)

    res = service.users().messages().list(
        userId="me",
        maxResults=10,
        q = "in:inbox is:unread category:primary",
    ).execute()

    output = []

    for msg in res.get("messages", []):
        data = service.users().messages().get(userId="me", id=msg["id"]).execute()
        headers = data["payload"]["headers"]

        subject = get_header(headers, "Subject", "(No Subject)")
        sender = get_header(headers, "From", "Unknown")

        body = extract_body(data["payload"])
        summary = summarize_email(body)

        output.append(
            {
                "id": msg["id"],
                "subject": subject,
                "from": sender,
                "summary": summary,
            }
        )

    return {"emails": output}
