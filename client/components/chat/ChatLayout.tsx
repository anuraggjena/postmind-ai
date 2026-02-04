"use client"

import Sidebar from "./Sidebar"
import ChatWindow from "./ChatWindow"

export default function ChatLayout() {
  return (
    <div className="h-screen w-full bg-black text-white flex">
      <Sidebar />
      <ChatWindow />
    </div>
  )
}
