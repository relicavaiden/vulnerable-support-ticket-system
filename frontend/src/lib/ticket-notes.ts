import type { TicketNote } from "@/lib/api";

export function getVisibleNotes(
    notes: TicketNote[]
): TicketNote[] {
    const latestStatusNote = [...notes]
        .reverse()
        .find((note) => note.note_type === "status_update");

    const visibleNotes = notes.filter((note) =>
        note.note_type !== "status_update" ||
        note.id === latestStatusNote?.id
    );

    return visibleNotes;
}