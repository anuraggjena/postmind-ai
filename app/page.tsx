export default function Home() {
  return (
    <main className="p-10">
      <h1 className="text-3xl font-bold">Constructure AI Email Assistant</h1>
      <p className="mt-4">Backend health check below:</p>
      <a href="/api/health" className="text-blue-600 underline">
        Check API
      </a>
    </main>
  );
}
