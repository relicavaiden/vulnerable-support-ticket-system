import type { TicketNote } from "@/lib/api"

type TicketNotesListProps = {
    notes: TicketNote[];
};

export default function TicketNotesList({
    notes,
}: TicketNotesListProps) {
    if (notes.length === 0) {
        return <p>No notes yet.</p>;
    }

    return (
        <ul>
            {notes.map((note) => (
                <li key={note.id}>
                    <p>{note.body}</p>
                    <p>Added by: {note.author_username}</p>
                    <p>Created: {note.created_at}</p>
                </li>
            ))}
        </ul>
    );
}