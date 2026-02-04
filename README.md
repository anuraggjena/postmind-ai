# 🧠 AI Gmail Assistant — Assignment Submission

A modern AI-powered Gmail assistant built with **FastAPI** and **Next.js** that allows users to:

* View summarized emails
* Generate AI replies
* Delete emails using natural language
* Confirm actions before execution
* Interact through a modern chatbot interface

The assistant understands commands like:

```
show my emails
reply to email 2
delete email from amazon
delete email number 3
```

---

## 🌐 Live Demo

**Frontend (Vercel)**
👉 [https://postmind-ai.vercel.app](https://postmind-ai.vercel.app)

**Backend (Render)**
👉 [https://postmind-ai.onrender.com](https://postmind-ai.onrender.com)

---

## 🧱 Tech Stack

| Layer        | Technology                                         |
| ------------ | -------------------------------------------------- |
| Frontend     | Next.js 15 (App Router), TailwindCSS, Lucide React |
| Backend      | FastAPI, Uvicorn                                   |
| Gmail Access | Google OAuth2 + Gmail API                          |
| AI           | Groq (Llama 3.1)                                   |
| HTML Parsing | BeautifulSoup                                      |
| Session Auth | Starlette Session Middleware                       |
| Hosting      | Vercel (frontend), Render (backend)                |

---

## ✨ Features Implemented

### ✅ Email Listing

* Fetches latest inbox emails
* Extracts clean body from MIME
* AI summarizes each email
* Sidebar preview with loading states

### ✅ Smart Delete (as required)

User can delete emails:

* By sender → *“delete latest email from amazon”*
* By subject keyword
* By number → *“delete email number 2”*

Flow:

1. Bot asks for confirmation
2. On confirmation → deletes from Gmail
3. Bot reports success/failure

### ✅ Smart Reply (as required)

1. Bot generates AI reply tied to the original email
2. Shows reply to user
3. Asks for confirmation
4. Sends via Gmail on confirmation
5. Reports success/failure

### ✅ Modern Chat UI

* Full width responsive chat
* Message bubbles
* Sidebar inbox preview
* Loading states
* User name greeting

---

## 🗂 Project Structure

```
root/
│
├── client/                 # Next.js frontend
│
├── api/
│   ├── main.py             # FastAPI entry
│   ├── routes/
│   │   ├── auth.py
│   │   ├── emails.py
│   │   └── chat.py
│   └── services/
│       ├── gmail_service.py
│       └── ai_service.py
│
├── requirements.txt
└── README.md
```

---

## ⚙️ Environment Variables

### Backend (.env on Render)

```
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
GROQ_API_KEY=...
SESSION_SECRET=super-secret-key
FRONTEND_URL=https://your-app-name.vercel.app
```

### Frontend (.env.local on Vercel)

```
NEXT_PUBLIC_API_URL=https://your-backend-name.onrender.com
```

---

## 🔐 Google OAuth & Gmail Setup

1. Go to Google Cloud Console
2. Create OAuth 2.0 credentials (Web Application)
3. Add Authorized Redirect URI:

```
https://your-backend-name.onrender.com/api/auth/callback
```

4. Enable APIs:

   * Gmail API
   * Google OAuth2 API

5. Download the OAuth JSON and place it at:

```
api/google_client.json
```

---

## 🖥 Running Locally

### Backend

```bash
pip install -r requirements.txt
uvicorn api.main:app --reload
```

### Frontend

```bash
cd client
npm install
npm run dev
```

---

## 📌 Assumptions & Limitations

* Works on latest emails (default: 5–10)
* Session based auth (not JWT)
* Requires Gmail OAuth each session expiry
* Designed for demonstration scale, not production scale
* Email parsing depends on MIME structure of Gmail messages

---

## 🎯 Assignment Requirements Coverage

| Requirement                | Status |
| -------------------------- | ------ |
| Delete by sender           | ✅      |
| Delete by subject          | ✅      |
| Delete by number           | ✅      |
| Confirmation before delete | ✅      |
| AI reply generation        | ✅      |
| Confirmation before reply  | ✅      |
| Report success/failure     | ✅      |
| Modern chatbot UI          | ✅      |
| Loading states             | ✅      |

---

## 🔐 OAuth Test User Note (Important for Review)

During development, Google OAuth requires all users to be explicitly added as Test Users in the Google Cloud Console when the app is in Testing mode.

The assignment mentions adding:

`test@gmail.com`

However, Google does not allow adding this address because it is not an active Google account.

As per the evaluation criteria, the reviewer account used for testing is:

`testingcheckuser1234@gmail.com`

This email has been added as a Test User in the Google Cloud OAuth configuration.

What this means for the reviewer

You can successfully:

- Log in with `testingcheckuser1234@gmail.com`

- View emails

- Reply to emails

- Delete emails

without any OAuth restriction.

If you wish to test with another account, simply add it as a Test User in:

Google Cloud Console → APIs & Services → OAuth Consent Screen → Test Users

---

## 🙌 Summary

This project demonstrates:

* Real Gmail integration
* Natural language command parsing
* AI-assisted email workflow
* Clean full-stack architecture
* Production style deployment (Vercel + Render)

---

**Built by:** Anurag Jena
