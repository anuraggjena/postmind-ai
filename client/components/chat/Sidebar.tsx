"use client";

import { Mail, Trash2 } from "lucide-react";
import { useEffect, useState } from "react";

export default function Sidebar() {
  const [emails, setEmails] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchEmails = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL}/api/emails`,
        { credentials: "include" }
      );
      const data = await res.json();
      setEmails(data.emails || []);
    } catch (e) {
      setEmails([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchEmails();
  }, []);

  const deleteEmail = async (id: string) => {
    await fetch(
      `${process.env.NEXT_PUBLIC_API_URL}/api/emails/${id}`,
      {
        method: "DELETE",
        credentials: "include",
      }
    );
    fetchEmails(); // refresh after delete
  };

  return (
    <div className="w-[32%] border-r border-neutral-800 p-6 overflow-y-auto">
      <div className="flex items-center gap-2 mb-6">
        <Mail size={20} />
        <h2 className="text-lg font-semibold">Inbox Preview</h2>
      </div>

      <div className="space-y-4">
        {/* Loading skeleton */}
        {loading &&
          [1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="animate-pulse bg-neutral-900 p-4 rounded-xl border border-neutral-800 space-y-3"
            >
              <div className="h-3 bg-neutral-700 rounded w-1/3" />
              <div className="h-4 bg-neutral-700 rounded w-3/4" />
              <div className="h-3 bg-neutral-800 rounded w-1/2" />
              <div className="h-3 bg-neutral-800 rounded w-full" />
            </div>
          ))}

        {/* Empty state */}
        {!loading && emails.length === 0 && (
          <div className="text-neutral-500 text-sm">
            No emails found.
          </div>
        )}

        {/* Emails */}
        {!loading &&
          emails.map((email, i) => (
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
                onClick={() => deleteEmail(email.id)}
              >
                <Trash2 size={14} /> Delete
              </button>
            </div>
          ))}
      </div>
    </div>
  );
}
