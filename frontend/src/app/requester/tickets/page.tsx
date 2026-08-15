"use client";

import { type SyntheticEvent, useState } from "react";

import LogoutButton from "@/components/LogoutButton";
import { createTicket, type TicketCategory } from "@/lib/api";
import TicketListItem from "@/components/tickets/TicketListItem";
import { useTicketList } from "@/hooks/useTicketList";
import CreateTicketForm from "@/components/tickets/CreateTicketForm";

export default function RequesterTicketsPage() {

    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [category, setCategory] = useState<TicketCategory | "">("");
    const [createError, setCreateError] = useState("");
    const [isCreating, setIsCreating] = useState(false);

    const {
        tickets,
        setTickets,
        isLoading,
    } = useTicketList({
        expectedRole: "requester",
        wrongRoleRedirect: "/resolver/tickets",
    });
    
    async function handleCreateTicket(event: SyntheticEvent<HTMLFormElement>) {
        event.preventDefault();

        if (!title.trim() || !description.trim() || !category) {
            setCreateError("Title, description, and category are required");
            return;
        }

        setCreateError("");
        setIsCreating(true);

        try {
            const createdTicket = await createTicket({
            title: title.trim(),
            description: description.trim(),
            category,
            });

            setTickets((currentTickets) => [...currentTickets, createdTicket.ticket]);

            setTitle("");
            setDescription("");
            setCategory("");
        } catch {
            setCreateError("Failed to create ticket. Please try again.");
        } finally {
            setIsCreating(false);
        }  
    }

    if (isLoading) {
        return <main>Loading...</main>;
    }


    return (
        <section className="space-y-8">
            <div>
                <h1 className="text-2xl font-semibold text-zinc-900">My Tickets</h1>
                
                <p className="mt-1 text-sm text-zinc-600">This is where requester tickets will appear.</p>
            </div>

            <div className="rounded-lg border border-zinc-200 bg-white p-6 shadow-sm">
                <CreateTicketForm
                    title={title}
                    description={description}
                    category={category}
                    createError={createError}
                    isCreating={isCreating}
                    onSubmit={handleCreateTicket}
                    onTitleChange={setTitle}
                    onDescriptionChange={setDescription}
                    onCategoryChange={setCategory}
                />
            </div>

            <div className="space-y-4">
                <h2 className="text-lg font-semibold text-zinc-900"> Submitted Tickets</h2>
            </div>


            {tickets.length === 0 ? (
                <p className="rounded-lg border border-dashed border-zinc-300 bg-white p-6 text-sm text-zinc-600">No tickets found.</p>
            ) : (
                <ul className="space-y-4">
                    {tickets.map((ticket) => (
                        <TicketListItem
                            key={ticket.id}
                            ticket={ticket}
                            href={`/requester/tickets/${ticket.id}`}
                        />
                    ))}
                </ul>
            )}
        </section>
    );
}