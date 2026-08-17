"use client";

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
        <section className="space-y-6">
            <div className="text-2xl font-semibold text-zinc-900">
                <h1>Resolver Tickets</h1>
                <p>Review and manage tickets assigned to you.</p>
            </div>

            {tickets.length === 0 ? (
                <p className="rounded-lg border border-dashed border-zinc-300 bg-white p-6 text-sm text-zinc-600">No tickets found.</p>
            ) : (
                <ul className="space-y-4">
                    {tickets.map((ticket) => (
                        <TicketListItem
                            key={ticket.id}
                            ticket={ticket}
                            href={`/resolver/tickets/${ticket.id}`}
                        />
                    ))}
                </ul>
            )}
        </section>
    );
}