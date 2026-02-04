"use client"

import { useEffect, useState } from "react"
import MessageBubble from "./MessageBubble"
import CommandInput from "./CommandInput"

export default function ChatWindow() {
  const [messages, setMessages] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [userName, setUserName] = useState("there")

  // 🔹 Fetch user name
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/me`, {
      credentials: "include",
    })
      .then(res => res.json())
      .then(data => {
        if (data.authenticated) {
          setUserName(data.user.name)
        }
      })
  }, [])

  // 🔹 Initial greeting (runs once when username ready)
  useEffect(() => {
    setMessages([
      {
        role: "ai",
        content: `Hi ${userName} 👋 I'm your AI Gmail assistant.

You can say things like:
• show my emails
• reply to email 1
• delete email from amazon
• delete email number 2`,
      },
    ])
  }, [userName])

  const sendMessage = async (msg: string) => {
    setMessages(prev => [...prev, { role: "user", content: msg }])

    setLoading(true)

    const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/chat`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: msg }),
    })

    const data = await res.json()

    setLoading(false)

    setMessages(prev => [
      ...prev,
      {
        role: "assistant",
        type: data.type,
        ...data.data,
      },
    ])
  }

  const handleAction = async (action: string, payload: any) => {
    if (action === "confirm_reply") {
      await sendMessage("yes send it")
    }

    if (action === "confirm_delete") {
      await sendMessage("yes delete it")
    }
  }

  return (
    <div className="flex-1 flex flex-col">
      <div className="flex-1 p-8 overflow-y-auto space-y-6">
        {messages.map((m, i) => (
          <MessageBubble
            key={i}
            message={m}
            onAction={handleAction}
          />
        ))}
      </div>

      <CommandInput onSend={sendMessage} loading={loading} />
    </div>
  )
}
