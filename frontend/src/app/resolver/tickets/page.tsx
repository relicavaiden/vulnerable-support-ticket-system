"use client";

import LogoutButton from "@/components/LogoutButton";
import TicketListItem from "@/components/tickets/TicketListItem";
import { useTicketList } from "@/hooks/useTicketList";

export default function ResolverTicketsPage() {

    const {
        tickets,
        isLoading,
    } = useTicketList({
        expectedRole: "resolver",
        wrongRoleRedirect: "/requester/tickets",
    });

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