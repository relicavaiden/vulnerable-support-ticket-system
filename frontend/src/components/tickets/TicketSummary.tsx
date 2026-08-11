import type { Ticket } from "@/lib/api";
import { formatCategory, formatStatus } from "@/lib/ticket-formatters";

type TicketSummaryProps = {
    ticket: Ticket;
};

export default function TicketSummary({
    ticket,
}: TicketSummaryProps) {
    return (
        <>
            <h1>{ticket.title}</h1>
            <p>{ticket.description}</p>
            <p>Status: {formatStatus(ticket.status)}</p>
            <p>Category: {formatCategory(ticket.category)}</p>
        </>
    );
}