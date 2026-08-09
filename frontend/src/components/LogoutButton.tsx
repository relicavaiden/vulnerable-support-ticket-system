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
            >
                {isLoggingOut ? "Logging out.." : "Logout"}
            </button>

            {logoutError && <p>{logoutError}</p>}
        </>
    )
}