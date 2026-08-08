"use client";

import { type SyntheticEvent, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { addTicketNote, getCurrentUser, getTicket, updateTicketStatus, type TicketDetail } from "@/lib/api";

export default function ResolverTicketDetailPage() {
    const [isLoading, setIsLoading] = useState(true);
    const [ticket, setTicket] = useState<TicketDetail | null>(null);
    const [loadError, setLoadError] = useState("");
    const [noteBody, setNoteBody] = useState("");
    const [noteError, setNoteError] = useState("");
    const [isAddingNote, setIsAddingNote] = useState(false);
    const [selectedStatus, setSelectedStatus] = useState<TicketDetail["status"]>("open");

    const [statusError, setStatusError] = useState("");
    const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
    
    const params = useParams<{ ticketId: string }>();
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

    async function handleAddNote(event: SyntheticEvent<HTMLFormElement>) {
        event.preventDefault();

        if (!noteBody.trim()) {
            setNoteError("Note body is required.");
            return;
        }

        if (ticket === null) {
            setNoteError("Ticket is unavailable.");
            return;
        }

        setNoteError("");
        setIsAddingNote(true);

        try {
            const createdNote = await addTicketNote(ticket.id, {
                body: noteBody.trim(),
            });

            setTicket((currentTicket) => {
                if (currentTicket === null) {
                    return null;
                }

                return {
                    ...currentTicket,
                    notes: [...currentTicket.notes, createdNote.note],
                };
            });

            setNoteBody("");
        } catch {
            setNoteError("Failed to add note. Please try again.");
        } finally {
            setIsAddingNote(false);
        }
    }

        async function handleStatusUpdate(event: SyntheticEvent<HTMLFormElement>) {
        event.preventDefault();

        if (ticket === null) {
            setStatusError("Ticket is unavailable.");
            return;
        }

        setStatusError("");
        setIsUpdatingStatus(true);

        try {
            await updateTicketStatus(ticket.id, {
                status: selectedStatus,
            });

            const refreshedTicket = await getTicket(ticket.id);

            setTicket(refreshedTicket.ticket);
            setSelectedStatus(refreshedTicket.ticket.status)
            } catch {
                setStatusError("Failed to update ticket status. Please try again.");
            } finally {
                setIsUpdatingStatus(false);
            }
}
    useEffect(() => {
        async function loadTicket() {
            try {
                const data = await getCurrentUser();
    
                if (data.user.role !== "resolver") {
                    router.replace("/requester/tickets");
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
                setSelectedStatus(ticketData.ticket.status);
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
                    <p>Status: {formatStatus(ticket.status)}</p>

                    <form onSubmit={handleStatusUpdate}>
                        <label htmlFor="status">Update Status</label>

                        <select
                            id="status"
                            name="status"
                            value={selectedStatus}
                            onChange={(event) =>
                                setSelectedStatus(event.target.value as TicketDetail["status"])
                            }
                        >
                            <option value="open">Open</option>
                            <option value="in_progress">In Progress</option>
                            <option value="resolved">Resolved</option>
                        </select>

                        {statusError && <p>{statusError}</p>}

                        <button type="submit" disabled={isUpdatingStatus}>
                            {isUpdatingStatus ? "Updating..." : "Update Status"}
                        </button>
                    </form>
                    <p>Category: {ticket.category}</p>
    
                    <h2>Notes</h2>
    
                    {ticket.notes.length === 0 ? (
                        <p>No notes yet.</p>
                    ) : (
                        <ul>
                            {ticket.notes.map((note) => (
                                <li key={note.id}>
                                    <p>{note.body}</p>
                                    <p>Added by: {note.author_username}</p>
                                    <p>Created: {note.created_at}</p>
                                </li>
                            ))}
                        </ul>
                    )}
                    <form onSubmit={handleAddNote}>
                            <h2>Add Resolver Note</h2>

                            <label htmlFor="noteBody">Note</label>
                            <textarea
                                id="noteBody"
                                name="noteBody"
                                value={noteBody}
                                onChange={(event) => setNoteBody(event.target.value)}
                            />

                            {noteError && <p>{noteError}</p>}

                            <button type="submit" disabled={isAddingNote}>
                                {isAddingNote ? "Adding note..." : "Add Note"}
                            </button>
                        </form>
                </main>
            );
        
}