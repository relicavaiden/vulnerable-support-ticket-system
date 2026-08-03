"use client";

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
        <main>
            <h1>Login</h1>

            <form onSubmit={handleSubmit}>
                <label htmlFor="username">Username</label>
                <input
                    id="username"
                    name="username"
                    value={username} 
                    onChange={(event) => setUsername(event.target.value)} 
                    type="text"
                    autoComplete="username"
                />

                <label htmlFor="password">Password</label>
                <input 
                    id="password"
                    name="password"
                    value={password} 
                    onChange={(event) => setPassword(event.target.value)} 
                    type="password"
                    autoComplete="current-password"
                />

                {error && <p>{error}</p>}
                
                <button type="submit">Log in</button>
            </form>
        </main>
    );
}