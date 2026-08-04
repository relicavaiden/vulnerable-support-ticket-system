"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getCurrentUser } from "@/lib/api";

export default function ResolverTicketsPage() {
    const [isLoading, setIsLoading] = useState(true);
    const router = useRouter();

    useEffect(() => {
        async function checkAuth() {
            try {
                const data = await getCurrentUser();

                if (data.user.role !== "resolver") {
                    router.replace("/requester/tickets");
                    return;
                }

                setIsLoading(false);
            } catch {
                router.replace("/login")
            }
        }

        checkAuth();
    }, [router]);

    if (isLoading) {
        return <main>Loading...</main>;
    }
    
    return (
        <main>
            <h1>Resolver Tickets</h1>
            <p>This is where assigned resolver tickets will appear.</p>
        </main>
    );
}