"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import LogoutButton from "@/components/LogoutButton";
import { getCurrentUser, getTickets, type Ticket } from "@/lib/api";
import { formatCategory, formatStatus } from "@/lib/ticket-formatters";

export default function ResolverTicketsPage() {
    const [isLoading, setIsLoading] = useState(true);
    const [tickets, setTickets] = useState<Ticket[]>([]);

    const router = useRouter();

    useEffect(() => {
        async function checkAuth() {
            try {
                const data = await getCurrentUser();

                if (data.user.role !== "resolver") {
                    router.replace("/requester/tickets");
                    return;
                }

                const ticketsData = await getTickets();
                setTickets(ticketsData.tickets);
                setIsLoading(false);
            } catch {
                router.replace("/login");
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
            <LogoutButton />
            <p>This is where assigned resolver tickets will appear.</p>

            {tickets.length === 0 ? (
                <p>No tickets found.</p>
            ) : (
                <ul>
                    {tickets.map((ticket) => (
                        <li key={ticket.id}>
                            <h2>
                                <Link href={`/resolver/tickets/${ticket.id}`}>
                                    {ticket.title}
                                </Link>
                            </h2>
                            <p>{ticket.description}</p>
                            <p>Status: {formatStatus(ticket.status)}</p>
                            <p>Category: {formatCategory(ticket.category)}</p>
                        </li>
                    ))}
                </ul>
            )}
        </main>
    );
}