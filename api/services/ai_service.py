import os
from groq import Groq


def get_groq_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))

def interpret_intent(text: str) -> str:
    client = get_groq_client()

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": """
                Classify the user intent into one of these:
                - greeting
                - show_emails
                - reply
                - delete
                - help
                - unknown

                Return only the label.
                """
            },
            {"role": "user", "content": text},
        ],
    )

    return res.choices[0].message.content.strip().lower()


def summarize_email(text: str) -> str:
    client = get_groq_client()

    text = text[:1500]

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "Summarize this email in 2 sentences."},
            {"role": "user", "content": text},
        ],
    )

    return res.choices[0].message.content


def generate_reply(text: str, name: str) -> str:
    client = get_groq_client()

    text = text[:1500]

    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": f"Write a professional email reply.\nEnd with:\nBest regards,\n{name}",
            },
            {"role": "user", "content": text},
        ],
    )

    return res.choices[0].message.content
