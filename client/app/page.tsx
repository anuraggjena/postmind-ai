import Link from "next/link";
import ParticlesBackground from "@/components/ParticlesBackground";

export default function Landing() {
  return (
    <main className="relative min-h-screen bg-black text-white overflow-hidden">
      <ParticlesBackground />

      <div className="absolute top-40 left-1/2 -translate-x-1/2 w-150 h-150 bg-purple-600/30 blur-[180px] rounded-full" />

      <nav className="relative z-10 flex items-center justify-between px-10 py-6">
        <h1 className="text-xl font-bold tracking-wide">Postmind AI</h1>
        <div className="flex gap-8 text-sm text-gray-300">
          <Link
            href="/login"
            className="bg-purple-600 px-5 py-2 rounded-lg text-white hover:bg-purple-700 transition"
          >
            Login
          </Link>
        </div>
      </nav>

      <section className="relative z-10 flex flex-col items-center text-center mt-30 px-6">
        <div className="mb-6 text-sm bg-white/10 border border-white/20 px-4 py-1 rounded-full backdrop-blur">
          ✨ AI Powered Gmail Assistant
        </div>

        <h2 className="text-6xl font-bold leading-tight max-w-4xl">
          Intelligent Email Automation for Modern Users.
        </h2>

        <p className="mt-8 text-gray-400 text-md max-w-2xl">
          Postmind uses AI to read, summarize, reply and manage your inbox
          using simple natural language commands.
        </p>

        <div className="mt-12 flex">
          <Link
            href="/login"
            className="bg-purple-600 px-8 rounded-lg text-white font-bold hover:bg-purple-700 transition"
          >
            Get Started
          </Link>
        </div>
      </section>
    </main>
  );
}
