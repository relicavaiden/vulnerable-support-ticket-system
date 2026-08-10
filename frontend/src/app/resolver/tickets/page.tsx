"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import LogoutButton from "@/components/LogoutButton";
import { getCurrentUser, getTickets, type Ticket } from "@/lib/api";
import TicketListItem from "@/components/tickets/TicketListItem";

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
                        <TicketListItem
                            key={ticket.id}
                            ticket={ticket}
                            href={`/resolver/tickets/${ticket.id}`}
                        />
                    ))}
                </ul>
            )}
        </main>
    );
}