"use client";

import { type SyntheticEvent, useState } from "react";
import { useParams } from "next/navigation";

import { addTicketNote, getTicket, updateTicketStatus, type TicketStatus } from "@/lib/api";
import { getVisibleNotes } from "@/lib/ticket-notes";
import TicketNotesList from "@/components/tickets/TicketNotesList";
import TicketSummary from "@/components/tickets/TicketSummary";
import TicketNoteForm from "@/components/tickets/TicketNoteForm";
import TicketStatusForm from "@/components/tickets/TicketStatusForm";
import { useTicketDetail } from "@/hooks/useTicketDetail";

export default function ResolverTicketDetailPage() {
    const [noteBody, setNoteBody] = useState("");
    const [noteError, setNoteError] = useState("");
    const [isAddingNote, setIsAddingNote] = useState(false);
    const [selectedStatus, setSelectedStatus] = useState<TicketStatus | null>(null);

    const [statusError, setStatusError] = useState("");
    const [isUpdatingStatus, setIsUpdatingStatus] = useState(false);
    
    const params = useParams();

    const {
        ticket,
        setTicket,
        loadError,
        isLoading,
    } = useTicketDetail({
        ticketId: params.ticketId as string,
        expectedRole: "resolver",
        wrongRoleRedirect: "/requester/tickets",
    });

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

        const newStatus = selectedStatus ?? ticket.status;

        setStatusError("");
        setIsUpdatingStatus(true);

        try {
            await updateTicketStatus(ticket.id, {
                status: newStatus,
            });

            const refreshedTicket = await getTicket(ticket.id);

            setTicket(refreshedTicket.ticket);
            setSelectedStatus(null)
            } catch {
                setStatusError("Failed to update ticket status. Please try again.");
            } finally {
                setIsUpdatingStatus(false);
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


            const statusSelection = selectedStatus ?? ticket.status;

            const visibleNotes = getVisibleNotes(ticket.notes);
    
            return (
                <main>
                    <TicketSummary ticket={ticket}/>

                    <TicketStatusForm
                        currentStatus={ticket.status}
                        selectedStatus={statusSelection}
                        statusError={statusError}
                        isUpdatingStatus={isUpdatingStatus}
                        onSubmit={handleStatusUpdate}
                        onStatusChange={setSelectedStatus}
                    />
    
                    <TicketNotesList notes={visibleNotes} />
                    <TicketNoteForm
                        heading="Add Resolver Note"
                        noteBody={noteBody}
                        noteError={noteError}
                        isAddingNote={isAddingNote}
                        onSubmit={handleAddNote}
                        onNoteBodyChange={setNoteBody}
                    />
                </main>
            );
        
}