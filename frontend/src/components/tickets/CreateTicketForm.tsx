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
        <form onSubmit={onSubmit}>

            <h2>Create Ticket</h2>

            <label htmlFor="title">Title</label>
            <input
                id="title"
                name="title"
                value={title}
                onChange={(event) => onTitleChange(event.target.value)}
                type="text"
            />

            <label htmlFor="description">Description</label>
            <textarea
                id="description"
                name="description"
                value={description}
                onChange={(event) => onDescriptionChange(event.target.value)}
            />

            <label htmlFor="category">Category</label>
            <select
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

            {createError && <p>{createError}</p>}

            <button type="submit" disabled={isCreating}>
                {isCreating ? "Creating..." : "Create Ticket"}
            </button>


        </form>
    );
}