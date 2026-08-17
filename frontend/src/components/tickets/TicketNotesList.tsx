import type { TicketNote } from "@/lib/api"

type TicketNotesListProps = {
    notes: TicketNote[];
};

export default function TicketNotesList({
    notes,
}: TicketNotesListProps) {
    return (
        <section className="space-y-4">
            <h2 className="text-lg font-semibold text-zinc-900">Notes</h2>
            
            {notes.length === 0 ? (
            <p className="rounded-lg border border-dashed border-zinc-300 bg-white p-5 text-sm text-zinc-600">No notes yet.</p>
            ) : (
            <ul className="space-y-3">
                {notes.map((note) => (
                    <li key={note.id} className="rounded-lg border border-zinc-200 bg-white p-4">
                        <p className="text-sm leading-6 text-zinc-800">{note.body}</p>
                        <div className="mt-3 space-y-1 text-xs text-zinc-500">
                            <p>Added by: {note.author_username}</p>
                            <p>Created: {note.created_at}</p>
                        </div>
                    </li>
                ))}
            </ul>
            )}
        </section>
    );
}