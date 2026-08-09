import type { TicketCategory, TicketStatus } from "./api";

export function formatStatus(status: TicketStatus) {
    if (status === "in_progress") return "In Progress";
    if (status === "resolved") return "Resolved";

    return "Open";
}

export function formatCategory(category: TicketCategory) {
    if (category === "account_access") return "Account Access";
    if (category === "hardware") return "Hardware";
    if (category === "software") return "Software";
    if (category === "network") return "Network";
    if (category === "other") return "Other";

    return category;
}