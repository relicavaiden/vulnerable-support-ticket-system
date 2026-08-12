"use client";

import { type SyntheticEvent, useState } from "react";

import LogoutButton from "@/components/LogoutButton";
import { createTicket, type TicketCategory } from "@/lib/api";
import TicketListItem from "@/components/tickets/TicketListItem";
import { useTicketList } from "@/hooks/useTicketList";

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
        <main>

            <h1>Requester Tickets</h1>
            <LogoutButton />
            <p>This is where requester tickets will appear.</p>

            <form onSubmit={handleCreateTicket}>
                <h2>Create Ticket</h2>

                <label htmlFor="title">Title</label>
                <input
                    id="title"
                    name="title"
                    value={title}
                    onChange={(event) => setTitle(event.target.value)}
                    type="text"
                />

                <label htmlFor="description">Description</label>
                <textarea
                    id="description"
                    name="description"
                    value={description}
                    onChange={(event) => setDescription(event.target.value)}
                />

                <label htmlFor="category">Category</label>
                <select
                    id="category"
                    name="category"
                    value={category}
                    onChange={(event) => setCategory(event.target.value as TicketCategory | "")}
                >
                    <option value="">Select a category</option>
                    <option value="account_access">Account Access</option>
                    <option value="hardware">Hardware</option>
                    <option value="software">Software</option>
                    <option value="network">Network</option>
                    <option value="other">Other</option>
                </select>

                {createError && <p>{createError}</p>}

                <button type="submit" disabled={isCreating}>{isCreating ? "Creating..." : "Create Ticket"}</button>
            </form>

            {tickets.length === 0 ? (
                <p>No tickets found.</p>
            ) : (
                <ul>
                    {tickets.map((ticket) => (
                        <TicketListItem
                            key={ticket.id}
                            ticket={ticket}
                            href={`/requester/tickets/${ticket.id}`}
                        />
                    ))}
                </ul>
            )}
        </main>
    );
}