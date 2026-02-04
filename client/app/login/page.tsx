"use client"

import ParticlesBackground from "@/components/ParticlesBackground"
import { Mail, Sparkles, ShieldCheck } from "lucide-react"

export default function LoginPage() {
  return (
    <div className="relative min-h-screen flex items-center justify-center bg-black text-white overflow-hidden">
      <ParticlesBackground />

      <div className="relative z-10 w-full max-w-md px-6">
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-10 shadow-2xl">

          <div className="flex flex-col items-center mb-6">
            <div className="bg-purple-600/20 p-3 rounded-full mb-4">
              <Sparkles className="w-6 h-6 text-white" />
            </div>

            <h1 className="text-2xl font-semibold text-center">
              Welcome to
            </h1>
            <h1 className="text-purple-400 text-3xl font-bold">Postmind AI</h1>

            <p className="text-gray-400 text-sm mt-6 text-center">
              Your intelligent Gmail assistant powered by AI
            </p>
          </div>

          <a
            href="https://postmind-ai.onrender.com/api/auth/login"
            className="w-full flex items-center justify-center gap-3 bg-white text-black font-medium py-3 rounded-lg hover:scale-105 transition-transform"
          >
            <Mail className="w-5 h-5" />
            Continue with Google
          </a>

          <div className="flex items-center justify-center gap-2 mt-6 text-xs text-gray-500">
            <ShieldCheck className="w-4 h-4" />
            Secure OAuth. No emails stored.
          </div>
        </div>
      </div>
    </div>
  )
}
