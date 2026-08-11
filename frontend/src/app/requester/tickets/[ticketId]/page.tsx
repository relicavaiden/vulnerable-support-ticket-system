"use client";

import { type SyntheticEvent, useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";

import { addTicketNote, getCurrentUser, getTicket, type TicketDetail } from "@/lib/api";
import { getVisibleNotes } from "@/lib/ticket-notes";
import TicketNotesList from "@/components/tickets/TicketNotesList";
import TicketSummary from "@/components/tickets/TicketSummary";
import TicketNoteForm from "@/components/tickets/TicketNoteForm";

export default function RequesterTicketDetail(){
    const [isLoading, setIsLoading] = useState(true);
    const [ticket, setTicket] = useState<TicketDetail | null>(null);
    const [loadError, setLoadError] = useState("");
    const [noteBody, setNoteBody] = useState("");
    const [noteError, setNoteError] = useState("");
    const [isAddingNote, setIsAddingNote] = useState(false);

    const params = useParams<{ ticketId: string }>();
    const router = useRouter();

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

        const visibleNotes = getVisibleNotes(ticket.notes);

        return (
            <main>
                <TicketSummary ticket={ticket}/>

                <h2>Notes</h2>

                <TicketNotesList notes={visibleNotes} />

                <TicketNoteForm
                    heading="Add Follow-Up Note"
                    noteBody={noteBody}
                    noteError={noteError}
                    isAddingNote={isAddingNote}
                    onSubmit={handleAddNote}
                    onNoteBodyChange={setNoteBody}
                />
            </main>
        );
    }