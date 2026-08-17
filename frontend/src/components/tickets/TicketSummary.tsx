import type { Ticket } from "@/lib/api";
import { formatCategory, formatStatus } from "@/lib/ticket-formatters";

type TicketSummaryProps = {
    ticket: Ticket;
};

export default function TicketSummary({
    ticket,
}: TicketSummaryProps) {
    return (
        <section className="rounded-lg border border-zinc-200 bg-white p-6 shadow-sm">
            <h1 className="text-2xl font-semibold text-zinc-900">{ticket.title}</h1>
            <p className="mt-3 text-sm leading-6 text-zinc-600">{ticket.description}</p>

            <div className="mt-5 flex flex-wrap gap-3 text-sm text-zinc-600">
                <span>Status: {formatStatus(ticket.status)}</span>
                <span>Category: {formatCategory(ticket.category)}</span>
            </div>
        </section>
    );
}