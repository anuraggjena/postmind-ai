"use client";

import { motion } from "framer-motion";

type Props = {
  message: any;
  onAction?: (action: string) => void;
};

export default function MessageBubble({ message, onAction }: Props) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.25 }}
      className={`flex ${isUser ? "justify-end" : "justify-start"}`}
    >
      <div
        className={`
          max-w-xl rounded-2xl px-5 py-4 shadow-md
          ${isUser
            ? "bg-purple-600 text-white"
            : "bg-zinc-900 text-zinc-200 border border-zinc-800"}
        `}
      >
        {/* USER TEXT */}
        {isUser && (
          <p className="whitespace-pre-wrap text-sm leading-relaxed">
            {message.content}
          </p>
        )}

        {/* NORMAL ASSISTANT TEXT */}
        {message.type === "text" && (
          <p className="whitespace-pre-wrap text-sm leading-relaxed">
            {message.data}
          </p>
        )}

        {/* EMAIL LIST */}
        {message.type === "emails" && (
          <div className="space-y-3">
            {message.data.map((e: any, i: number) => (
              <div
                key={i}
                className="p-3 rounded-lg bg-zinc-800 border border-zinc-700"
              >
                <p className="font-semibold text-sm">{e.subject}</p>
                <p className="text-xs text-zinc-400">{e.from}</p>
                <p className="text-xs mt-2 text-zinc-300">{e.summary}</p>
              </div>
            ))}
          </div>
        )}

        {/* REPLY PREVIEW */}
        {message.type === "reply_preview" && (
          <div className="space-y-3">
            <p className="text-xs text-zinc-400">
              Reply to:{" "}
              <span className="text-zinc-200">
                {message.data.original_subject}
              </span>
            </p>

            <div className="p-3 rounded-lg bg-zinc-800 border border-zinc-700 text-sm whitespace-pre-wrap">
              {message.data.reply}
            </div>

            <button
              onClick={() => onAction?.("confirm_reply")}
              className="mt-2 px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm"
            >
              Send this reply
            </button>
          </div>
        )}

        {/* DELETE CONFIRMATION TEXT */}
        {message.type === "confirm_delete" && (
          <button
            onClick={() => onAction?.("confirm_delete")}
            className="mt-2 px-4 py-2 bg-red-600 hover:bg-red-700 rounded-lg text-sm"
          >
            Confirm delete
          </button>
        )}

        {/* TIME */}
        <p className="text-[10px] text-zinc-500 mt-2 text-right">
          {new Date(message.time).toLocaleTimeString()}
        </p>
      </div>
    </motion.div>
  );
}
