"use client"

import { Mail, Trash2 } from "lucide-react"
import { useEffect, useState } from "react"

export default function Sidebar() {
  const [emails, setEmails] = useState<any[]>([])
  
  useEffect(() => {
    fetch("/api/emails", {
      credentials: "include",
    })
      .then(res => res.json())
      .then(data => setEmails(data.emails))
  }, [])

  return (
    <div className="w-[32%] border-r border-neutral-800 p-6 overflow-y-auto">
      <div className="flex items-center gap-2 mb-6">
        <Mail size={20} />
        <h2 className="text-lg font-semibold">Inbox Preview</h2>
      </div>

      <div className="space-y-4">
        {emails.map((email, i) => (
          <div
            key={email.id}
            className="bg-neutral-900 p-4 rounded-xl hover:bg-neutral-800 transition"
          >
            <p className="text-sm text-neutral-400">Email {i + 1}</p>
            <h3 className="font-semibold">{email.subject}</h3>
            <p className="text-sm text-neutral-400">{email.from}</p>
            <p className="text-sm mt-2">{email.summary}</p>

            <button
              className="mt-3 text-red-400 flex items-center gap-1 text-sm"
              onClick={() =>
                fetch(`/api/emails/${email.id}`, {
                  method: "DELETE",
                  credentials: "include",
                })
              }
            >
              <Trash2 size={14} /> Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  )
}
