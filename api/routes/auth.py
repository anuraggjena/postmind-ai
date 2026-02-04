import os
from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

router = APIRouter()

CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

SCOPES = [
    "openid",
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.modify",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def get_flow():
    return Flow.from_client_secrets_file(
        "api/google_client.json",
        scopes=SCOPES,
        redirect_uri="https://postmind-ai.vercel.app/api/auth/callback",
    )


@router.get("/api/auth/login")
async def login():
    flow = get_flow()
    url, _ = flow.authorization_url(prompt="consent")

    print("Login URL:", url)  # Debugging line to print the URL
    return RedirectResponse(url)


@router.get("/api/auth/callback")
async def callback(request: Request, code: str):
    flow = get_flow()
    flow.fetch_token(code=code)

    creds = flow.credentials
    oauth = build("oauth2", "v2", credentials=creds)
    info = oauth.userinfo().get().execute()

    # store full creds
    request.session["user"] = {
        "email": info["email"],
        "name": info["name"],
        "creds": {
            "token": creds.token,
            "refresh_token": creds.refresh_token,
            "token_uri": creds.token_uri,
            "client_id": creds.client_id,
            "client_secret": creds.client_secret,
            "scopes": creds.scopes,
        }
    }

    return RedirectResponse("http://localhost:3000/chat")



@router.get("/api/me")
async def me(request: Request):
    user = request.session.get("user")
    if not user:
        return {"authenticated": False}
    return {"authenticated": True, "user": user}
