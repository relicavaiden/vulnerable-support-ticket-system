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
        <li className="rounded-lg border border-zinc-200 bg-white p-5 shadow-sm">
            <h2 className="text-lg font-semibold text-zinc-900">
                <Link href={href}>
                    {ticket.title}
                </Link>
            </h2>
            <p className="mt-2 text-sm text-zinc-600">{ticket.description}</p>
            <div className="mt-4 flex flex-wrap gap-2 text-sm text-zinc-600">
                <p>Status: {formatStatus(ticket.status)}</p>
                <p>Category: {formatCategory(ticket.category)}</p>
            </div>
        </li>
    );
}