"use client";

import { type SyntheticEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import LogoutButton from "@/components/LogoutButton";
import { createTicket, getCurrentUser, getTickets, TicketCategory, type Ticket } from "@/lib/api";
import TicketListItem from "@/components/tickets/TicketListItem";

export default function RequesterTicketsPage() {

    const [isLoading, setIsLoading] = useState(true);
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [category, setCategory] = useState<TicketCategory | "">("");
    const [createError, setCreateError] = useState("");
    const [isCreating, setIsCreating] = useState(false);

    const router = useRouter();
    
    async function handleCreateTicket(event: SyntheticEvent<HTMLFormElement>) {
        event.preventDefault();

        if (!title.trim() || !description.trim() || !category) {
            setCreateError("Title, description, and category are required");
            return;
        }

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
            setCreateError("");
            setIsCreating(false);
        }  
    }

    useEffect(() => {
        async function checkAuth() {
            try {
                const data = await getCurrentUser();

                if (data.user.role !== "requester") {
                    router.replace("/resolver/tickets");
                    return;
                }

                const ticketsData = await getTickets();
                setTickets(ticketsData.tickets);
                setIsLoading(false);
            } catch {
                router.replace("/login");
            }
        }

        checkAuth();
    }, [router]);


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