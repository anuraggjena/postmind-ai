# Postmind AI — Intelligent Gmail Assistant

Postmind AI is an AI-powered Gmail assistant that allows users to manage their inbox using natural language commands through a chat interface.

Users can:
- View emails with AI summaries
- Reply to emails with AI-generated responses
- Delete emails by number, sender, or subject
- Confirm actions before execution

---

## Live URL

https://postmind-ai.vercel.app

---

## Tech Stack

Frontend:
- Next.js
- Tailwind CSS
- React

Backend:
- FastAPI
- Gmail API
- Google OAuth 2.0
- Groq (LLaMA 3.1)
- BeautifulSoup

Deployment:
- Vercel (Fullstack)

---

## Setup Instructions

### Clone

```bash
git clone <repo>
cd postmind-ai
```

### Install Frontend

```bash
cd client
npm install
npm run dev
```

### Run Backend

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload
```

---

## Google OAuth Setup

1. Create OAuth Client (Web Application)
2. Add Redirect URIs:

```
http://localhost:8000/api/auth/callback
https://your-app-name.vercel.app/api/auth/callback
```

3. Place downloaded JSON at:

```
api/google_client.json
```

---

## Environment Variables (Vercel)

```
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
GOOGLE_REDIRECT_URI=
GROQ_API_KEY=
SESSION_SECRET=
```

---

## Supported Commands

- show my emails
- reply to email 1
- delete email number 2
- delete email from amazon
- delete email with subject invoice

System asks confirmation before delete or reply.

---

## Assumptions & Limitations

- Works on latest 5–10 emails
- Depends on Gmail API quotas
- Requires valid Google OAuth credentials
- Groq API key required for AI responses
