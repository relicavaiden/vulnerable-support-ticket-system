"use client";

import { type SyntheticEvent, useState } from "react";
import { useParams } from "next/navigation";

import { addTicketNote } from "@/lib/api";
import { getVisibleNotes } from "@/lib/ticket-notes";
import TicketNotesList from "@/components/tickets/TicketNotesList";
import TicketSummary from "@/components/tickets/TicketSummary";
import TicketNoteForm from "@/components/tickets/TicketNoteForm";
import { useTicketDetail } from "@/hooks/useTicketDetail";

export default function RequesterTicketDetail(){
    const [noteBody, setNoteBody] = useState("");
    const [noteError, setNoteError] = useState("");
    const [isAddingNote, setIsAddingNote] = useState(false);

    const params = useParams();

    const {
        ticket,
        setTicket,
        loadError,
        isLoading,
    } = useTicketDetail({
        ticketId: params.ticketId as string,
        expectedRole: "requester",
        wrongRoleRedirect: "/resolver/tickets",
    })

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