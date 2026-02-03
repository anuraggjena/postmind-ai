"use client";

import { useEffect, useState } from "react";

export default function ChatPage() {
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    fetch("http://localhost:8000/api/me", {
      credentials: "include",
    })
      .then((res) => res.json())
      .then((data) => {
        if (data.authenticated) setUser(data.user);
      });
  }, []);

  if (!user) return <div className="p-10">Loading...</div>;

  return (
    <main className="p-10">
      <h1 className="text-2xl font-bold">Welcome {user.name}</h1>
      <p>{user.email}</p>
    </main>
  );
}
