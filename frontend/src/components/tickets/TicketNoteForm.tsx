import type { SubmitEventHandler } from "react";

type TicketNoteFormProps = {
    heading: string;
    noteBody: string;
    noteError: string;
    isAddingNote: boolean;
    onSubmit: SubmitEventHandler<HTMLFormElement>;
    onNoteBodyChange: (value: string) => void;
};

export default function TicketNoteForm({
    heading,
    noteBody,
    noteError,
    isAddingNote,
    onSubmit,
    onNoteBodyChange,
}: TicketNoteFormProps) {
    return (
        <form onSubmit={onSubmit}>
            <h2>{heading}</h2>

            <label htmlFor="noteBody">Note</label>

            <textarea
                id="noteBody"
                name="noteBody"
                value={noteBody}
                onChange={(event) =>
                    onNoteBodyChange(event.target.value)
                }
            />

            {noteError && <p>{noteError}</p>}

            <button
                type="submit"
                disabled={isAddingNote}
                >
                    {isAddingNote ? "Adding note..." : "Add Note"}
                </button>
        </form>
    )
};