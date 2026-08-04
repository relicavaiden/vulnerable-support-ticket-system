"use client"

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getCurrentUser } from "@/lib/api"

export default function RequesterTicketsPage() {

    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        async function checkAuth() {
            try {
                const data = await getCurrentUser();

                if (data.user.role !== "requester") {
                    router.replace("/resolver/tickets");
                    return;
                }

                setIsLoading(false);
            } catch {
                router.push("/login");
            }
        }

        checkAuth();
    }, [router]);

    if (isLoading) {
        return <main>Loading...</main>
    }


    return (
        <main>
            <h1>Requester Tickets</h1>
            <p>This is where requester tickets will appear.</p>
        </main>
    );
}