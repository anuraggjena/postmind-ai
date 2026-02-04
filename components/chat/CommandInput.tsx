"use client"

import { useState } from "react"

export default function CommandInput({ onSend, loading }: any) {
  const [text, setText] = useState("")

  return (
    <div className="border-t border-neutral-800 p-4 flex gap-3">
      <input
        disabled={loading}
        value={text}
        onChange={e => setText(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === "Enter" && !loading) {
            onSend(text)
            setText("")
          }
        }}
        placeholder="Type: show my emails | reply to email 2 | delete email 1"
        className="flex-1 bg-neutral-900 p-3 rounded-lg outline-none disabled:opacity-50"
      />
      <button
        disabled={loading}
        onClick={() => {
          onSend(text)
          setText("")
        }}
        className="bg-purple-600 px-6 rounded-lg disabled:opacity-50"
      >
        {loading ? "Thinking..." : "Send"}
      </button>
    </div>
  )
}
