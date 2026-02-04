from pathlib import Path
from dotenv import load_dotenv
import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from api.routes.auth import router as auth_router
from api.routes.emails import router as emails_router
from api.routes.chat import router as chat_router

print("RUNNING THIS MAIN:", __file__)

app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

print("GOOGLE_CLIENT_ID:", os.getenv("GOOGLE_CLIENT_ID"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret-key",
    same_site="lax",
    https_only=False,
)

app.include_router(auth_router)
app.include_router(emails_router)
app.include_router(chat_router)
