import type { SubmitEventHandler } from "react";

import type { TicketStatus } from "@/lib/api";

type TicketStatusFormProps = {
    currentStatus: TicketStatus;
    selectedStatus: TicketStatus;
    statusError: string;
    isUpdatingStatus: boolean;
    onSubmit: SubmitEventHandler<HTMLFormElement>;
    onStatusChange: (status: TicketStatus) => void;
};

export default function TicketStatusForm({
    currentStatus,
    selectedStatus,
    statusError,
    isUpdatingStatus,
    onSubmit,
    onStatusChange,
}: TicketStatusFormProps ) {
    return (
        <form onSubmit={onSubmit} className="space-y-4">
            <h2 className="text-lg font-semibold text-zinc-900">Update Status</h2>

            <div className="space-y-2">
                <label htmlFor="ticketStatus" className="space-y-2">Status: </label>

                <select className="w-full rounded border border-zinc-300 bg-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-zinc-400"
                    id="status"
                    name="status"
                    value={selectedStatus}
                    onChange={(event) =>
                        onStatusChange(event.target.value as TicketStatus)
                    }
                >
                    <option value="open">Open</option>
                    <option value="in_progress">In Progress</option>
                    <option value="resolved">Resolved</option>
                </select>
            </div>

            {statusError && <p className="text-sm text-red-600">{statusError}</p>}

            <button type="submit" disabled={isUpdatingStatus || selectedStatus === currentStatus} className="rounded-md bg-zinc-900 px-4 py-2 text-sm font-medium text-white disabled:cursor-not-allowed disabled:opacity-50">
                {isUpdatingStatus ? "Updating..." : "Update Status"}
            </button>
        </form>
    );
}