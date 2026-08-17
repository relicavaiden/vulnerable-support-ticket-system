"use client";

const appVersion = process.env.NEXT_PUBLIC_APP_VERSION ?? "V1"

import { useState } from "react";
import { useRouter } from "next/navigation";

import { login } from "@/lib/api";

export default function LoginPage() {
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [error, setError] = useState("");

    const router = useRouter();

    async function handleSubmit(event: { preventDefault: () => void}) {
        event.preventDefault();

        try {
            setError("");

            const data = await login(username, password);

            if (data.user.role === "requester") {
                router.push("/requester/tickets");
            } else {
                router.push("/resolver/tickets");
            }
        } catch {
            setError("Invalid username or password");
        }
    }

    return (
        <main className="flex min-h-screen items-center justify-center bg-zinc-50 px-6">
            <section className="w-full max-w-md rounded-lg border border-zinc-200 bg-white p-8 shadow-sm">
                <div className="mb-8 space-y-3 text-center">
                    <h1 className="text-2xl font-semibold text-zinc-900">Vulnerable Support Ticket System</h1>

                    <span className="inline-flex rounded-full border border-zinc-300 px-3 py-1 text-xs font-medium text-zinc-600">
                        {appVersion}
                    </span>
                </div>

                <form onSubmit={handleSubmit} className="space-y-5">
                    <div className="space-y-2">
                        <label htmlFor="username" className="text-sm font-medium text-zinc-700">Username</label>
                        <input className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-400"
                            id="username"
                            name="username"
                            value={username} 
                            onChange={(event) => setUsername(event.target.value)} 
                            type="text"
                            autoComplete="username"
                        />

                        <label htmlFor="password" className="text-sm font-medium text-zinc-700">Password</label>
                        <input className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-400"
                            id="password"
                            name="password"
                            value={password} 
                            onChange={(event) => setPassword(event.target.value)} 
                            type="password"
                            autoComplete="current-password"
                        />
                </div>

                {error && <p className="text-sm text-red-600">{error}</p>}
                
                <button type="submit" className="w-full rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabed:opacity-50">Log in</button>
            </form>
            </section>
        </main>
    );
}