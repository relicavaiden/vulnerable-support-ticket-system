"use client";

import { type SyntheticEvent, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { createTicket, getCurrentUser, getTickets, type Ticket } from "@/lib/api";

export default function RequesterTicketsPage() {

    const [isLoading, setIsLoading] = useState(true);
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [category, setCategory] = useState("");

    const router = useRouter();
    
    async function handleCreateTicket(event: SyntheticEvent<HTMLFormElement>) {
        event.preventDefault();

        if (!title.trim() || !description.trim() || !category) {
            return;
        }

        const createdTicket = await createTicket({
            title,
            description,
            category,
        });

        setTickets((currentTickets) => [...currentTickets, createdTicket.ticket]);

        setTitle("");
        setDescription("");
        setCategory("");
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
                    onChange={(event) => setCategory(event.target.value)}
                >
                    <option value="">Select a category</option>
                    <option value="account_access">Account Access</option>
                    <option value="hardware">Hardware</option>
                    <option value="software">Software</option>
                    <option value="network">Network</option>
                    <option value="other">Other</option>
                </select>

                <button type="submit">Create Ticket</button>
            </form>

            {tickets.length === 0 ? (
                <p>No tickets found.</p>
            ) : (
                <ul>
                    {tickets.map((ticket) => (
                        <li key={ticket.id}>
                            <h2>{ticket.title}</h2>
                            <p>{ticket.description}</p>
                            <p>Status: {ticket.status}</p>
                            <p>Category: {ticket.category}</p>
                        </li>
                    ))}
                </ul>
            )}
        </main>
    );
}