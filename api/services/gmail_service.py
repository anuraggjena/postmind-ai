import base64
import re
from bs4 import BeautifulSoup
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials


def get_gmail_service(user):
    creds_data = user["creds"]

    creds = Credentials(
        token=creds_data["token"],
        refresh_token=creds_data["refresh_token"],
        token_uri=creds_data["token_uri"],
        client_id=creds_data["client_id"],
        client_secret=creds_data["client_secret"],
        scopes=creds_data["scopes"],
    )

    return build("gmail", "v1", credentials=creds)


def get_header(headers, name, default=""):
    for h in headers:
        if h["name"] == name:
            return h["value"]
    return default


def extract_body(payload):
    plain_text = None
    html_text = None

    def walk(part):
        nonlocal plain_text, html_text

        mime = part.get("mimeType", "")
        body = part.get("body", {}).get("data")

        if mime == "text/plain" and body and not plain_text:
            plain_text = base64.urlsafe_b64decode(body).decode("utf-8", errors="ignore")

        elif mime == "text/html" and body and not html_text:
            html = base64.urlsafe_b64decode(body).decode("utf-8", errors="ignore")
            soup = BeautifulSoup(html, "html.parser")
            html_text = soup.get_text(separator="\n")

        for p in part.get("parts", []) or []:
            walk(p)

    walk(payload)
    text = plain_text if plain_text else html_text if html_text else ""
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def build_email_map(service, limit=10):
    res = service.users().messages().list(
        userId="me",
        maxResults=limit,
        labelIds=["INBOX", "CATEGORY_UPDATES"],
    ).execute()

    email_map = {}
    for idx, msg in enumerate(res.get("messages", []), start=1):
        email_map[str(idx)] = msg["id"]

    return email_map