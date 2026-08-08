"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getCurrentUser, getTickets, TicketDetail, type Ticket } from "@/lib/api";

export default function ResolverTicketsPage() {
    const [isLoading, setIsLoading] = useState(true);
    const [tickets, setTickets] = useState<Ticket[]>([]);

    const router = useRouter();

            function formatStatus(status: TicketDetail["status"]) {
            if (status === "in_progress") {
                return "In Progress";
            }
    
            if (status == "resolved") {
                return "Resolved";
            }
    
            return "Open";
        }

            function formatCategory(category: TicketDetail["category"]) {
            if (category === "account_access") {
                return "Account Access";
            }

            if (category === "hardware") {
                return "Hardware";
            }

            if (category === "software") {
                return "Software";
            }

            if (category === "network") {
                return "Network";
            }

            if (category === "other") {
                return "Other";
            }

            return category;
        }

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