import os
from fastapi import APIRouter, Request, HTTPException
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
    if not user:
        raise HTTPException(status_code=401, detail="Not authenticated")

    service = get_gmail_service(user)

    query = None
    if unread:
        query = "is:unread category:primary"

    res = service.users().messages().list(
        userId="me",
        maxResults=5,
        labelIds=["INBOX"],
        q=query,
    ).execute()

    output = []

    for msg in res.get("messages", []):
        data = service.users().messages().get(
            userId="me",
            id=msg["id"]
        ).execute()

        headers = data["payload"]["headers"]

        subject = get_header(headers, "Subject", "(No Subject)")
        sender = get_header(headers, "From", "Unknown")

        body = extract_body(data["payload"])

        output.append(
            {
                "id": msg["id"],
                "subject": subject,
                "from": sender,
                "summary": body[:200],
            }
        )

    return {"emails": output}