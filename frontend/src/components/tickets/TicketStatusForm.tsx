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
        <form onSubmit={onSubmit}>
            <label htmlFor="status">Update Status</label>

            <select
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

            {statusError && <p>{statusError}</p>}

            <button type="submit" disabled={isUpdatingStatus || selectedStatus === currentStatus}>
                {isUpdatingStatus ? "Updating..." : "Update Status"}
            </button>
        </form>
    );
}