"use client"

import { useEffect, useRef, useState } from "react"
import MessageBubble from "./MessageBubble"
import CommandInput from "./CommandInput"

export default function ChatWindow() {
  const [messages, setMessages] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [userName, setUserName] = useState("there")

  const bottomRef = useRef<HTMLDivElement>(null)

  // 🔹 Auto scroll whenever messages or loading changes
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages, loading])

  // Fetch user
  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/me`, {
      credentials: "include",
    })
      .then(res => res.json())
      .then(data => {
        if (data.authenticated) setUserName(data.user.name)
      })
  }, [])

  // Initial greeting
  useEffect(() => {
    setMessages([
      {
        role: "assistant",
        type: "text",
        data: `Hi ${userName} 👋 I'm your AI Gmail assistant.

You can say:
• show my emails
• reply to email 1
• delete email from <sender>`,
        time: Date.now(),
      },
    ])
  }, [userName])

  const sendMessage = async (msg: string) => {
    setMessages(prev => [
      ...prev,
      { role: "user", content: msg, time: Date.now() },
    ])

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
        data: data.data,
        time: Date.now(),
      },
    ])

    // 🔥 Refresh sidebar if deleted
    if (
      data.type === "text" &&
      typeof data.data === "string" &&
      data.data.toLowerCase().includes("deleted")
    ) {
      window.dispatchEvent(new Event("refreshEmails"))
    }
  }

  const handleAction = async (action: string) => {
    if (action === "confirm_reply") {
      await sendMessage("yes")
    }

    if (action === "confirm_delete") {
      await sendMessage("yes")
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

        {loading && (
          <div className="text-sm text-zinc-400">Thinking...</div>
        )}

        {/* 🔹 Scroll Anchor */}
        <div ref={bottomRef} />
      </div>

      <CommandInput onSend={sendMessage} loading={loading} />
    </div>
  )
}
