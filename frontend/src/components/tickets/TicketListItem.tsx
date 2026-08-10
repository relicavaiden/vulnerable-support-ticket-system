import Link from "next/link";

import type { Ticket } from "@/lib/api";
import { formatCategory, formatStatus } from "@/lib/ticket-formatters";

type TicketListItemProps = {
    ticket: Ticket;
    href: string;
};

export default function TicketListItem ({
    ticket,
    href,
}: TicketListItemProps) {
    return (
        <li>
            <h2>
                <Link href={href}>
                    {ticket.title}
                </Link>
            </h2>
            <p>{ticket.description}</p>
            <p>Status: {formatStatus(ticket.status)}</p>
            <p>Category: {formatCategory(ticket.category)}</p>
        </li>
    );
}