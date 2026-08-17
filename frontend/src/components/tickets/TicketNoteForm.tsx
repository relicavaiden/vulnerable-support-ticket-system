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
        <form onSubmit={onSubmit} className="space-y-4">
            <h2 className="text-lg font-semibold text-zinc-900">{heading}</h2>

            <div className="space-y-2">

                <label htmlFor="noteBody" className="text-sm font-medium text-zinc-700">Note</label>

                <textarea className="w-full rounded-md border border-zinc-300 bg-white px-3 py-2 text-zinc-900 focus:ring-2 focus:ring-zinc-400"
                    id="noteBody"
                    name="noteBody"
                    value={noteBody}
                    onChange={(event) =>
                        onNoteBodyChange(event.target.value)
                    }
                />
            </div>

            {noteError && <p className="text-sm text-red-600">{noteError}</p>}

            <button
                type="submit"
                disabled={isAddingNote}
                className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50"
                >
                    {isAddingNote ? "Adding note..." : "Add Note"}
                </button>
        </form>
    )
};