import type { SubmitEventHandler } from "react";
import type { TicketCategory } from "@/lib/api";

type CreateTicketFormProps = {
    title: string;
    description: string;
    category: TicketCategory | "";
    createError: string;
    isCreating: boolean;
    onSubmit: SubmitEventHandler<HTMLFormElement>;
    onTitleChange: (value: string) => void;
    onDescriptionChange: (value: string) => void;
    onCategoryChange: (value: TicketCategory | "") => void;
}

export default function CreateTicketForm({
    title,
    description,
    category,
    createError,
    isCreating,
    onSubmit,
    onTitleChange,
    onDescriptionChange,
    onCategoryChange,
}: CreateTicketFormProps){
    return (
        <form onSubmit={onSubmit} className="space-y-5">

            <h2>Create Ticket</h2>

            <div className="space-y-2">
                <label htmlFor="title">Title</label>
                <input className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-zinc-900 focus:outline-none focus:ring-2 focus:ring-zinc-400"
                    id="title"
                    name="title"
                    value={title}
                    onChange={(event) => onTitleChange(event.target.value)}
                    type="text"
                />
            </div>

            <div className="space-y-2">
                <label htmlFor="description">Description</label>
                <textarea className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-zinc-900 focus:outline-none foucs:ring-2 focus:ring-zinc-400"
                    id="description"
                    name="description"
                    value={description}
                    onChange={(event) => onDescriptionChange(event.target.value)}
                />
            </div>

            <div className="space-y-2">
                <label htmlFor="category">Category</label>
                <select className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 focus:outline-none focus:ring-2 focus:ring-zinc-400"
                    id="category"
                    name="category"
                    value={category}
                    onChange={(event) => onCategoryChange(event.target.value as TicketCategory | "")}
                >
                    <option value="">Select a category</option>
                    <option value="account_access">Account Access</option>
                    <option value="hardware">Hardware</option>
                    <option value="software">Software</option>
                    <option value="network">Network</option>
                    <option value="other">Other</option>
                </select>
            </div>

            {createError && <p className="text-sm text-red-600">{createError}</p>}

            <button type="submit" disabled={isCreating} className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50">
                {isCreating ? "Creating..." : "Create Ticket"}
            </button>


        </form>
    );
}