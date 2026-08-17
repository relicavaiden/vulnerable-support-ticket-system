"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { logout } from "@/lib/api";

export default function LogoutButton() {
    const [logoutError, setLogoutError] = useState("");
    const [isLoggingOut, setIsLoggingOut] = useState(false);

    const router = useRouter();

    async function handleLogout() {
        setLogoutError("");
        setIsLoggingOut(true);

        try {
            await logout();
            router.replace("/login");
        } catch {
            setLogoutError("Failed to log out. Please try again.");
            setIsLoggingOut(false);
        }
    }

    return (
        <>
            <button
                type="button"
                onClick={handleLogout}
                disabled={isLoggingOut}
                className="rounded-md border-2 bg-zinc-900 px-4 py-2 text-sm font-medium text-white"
            >
                {isLoggingOut ? "Logging out.." : "Logout"}
            </button>

            {logoutError && <p className="text-sm text-red-600">{logoutError}</p>}
        </>
    )
}