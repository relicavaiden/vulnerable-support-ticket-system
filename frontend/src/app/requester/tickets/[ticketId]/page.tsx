"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { getCurrentUser, getTicket, type TicketDetail } from "@/lib/api";

export default function RequesterTicketDetail(){
    const [isLoading, setIsLoading] = useState(true);
    const [ticket, setTicket] = useState<TicketDetail | null>(null);
    const [loadError, setLoadError] = useState("");

    const params = useParams<{ ticketId: string }>();
    const router = useRouter();

    useEffect(() => {
        async function loadTicket() {
            try {
                const data = await getCurrentUser();

                if (data.user.role !== "requester") {
                    router.replace("/resolver/tickets");
                    return;
                }

                const numericTicketId = Number(params.ticketId);

                if (Number.isNaN(numericTicketId)) {
                    setLoadError("Invalid ticket id.");
                    setIsLoading(false);
                    return;
                }

                const ticketData = await getTicket(numericTicketId);
                setTicket(ticketData.ticket);
                setIsLoading(false);
            } catch {
                setLoadError("Failed to load ticket.");
                setIsLoading(false);
            }
        }

        loadTicket();
    }, [params.ticketId, router]);

    if (isLoading) {
        return <main>Loading ticket...</main>;
        }

        if (loadError) {
            return <main>{loadError}</main>;
        }

        if (ticket === null) {
            return <main>Ticket not found.</main>;
        }

        return (
            <main>
                <h1>{ticket.title}</h1>

                <p>{ticket.description}</p>
                <p>Status: {ticket.status}</p>
                <p>Category: {ticket.category}</p>

                <h2>Notes</h2>

                {ticket.notes.length === 0 ? (
                    <p>No notes yet.</p>
                ) : (
                    <ul>
                        {ticket.notes.map((note) => (
                            <li key={note.id}>
                                <p>{note.body}</p>
                                <p>Type: {note.note_type}</p>
                                <p>Created: {note.created_at}</p>
                            </li>
                        ))}
                    </ul>
                )}
            </main>
        );
    }
