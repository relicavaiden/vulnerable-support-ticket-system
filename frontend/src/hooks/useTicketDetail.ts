"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getCurrentUser, getTicket } from "@/lib/api";

import type { TicketDetail, UserRole } from "@/lib/api";

type UseTicketDetailOptions = {
    ticketId: string;
    expectedRole: UserRole;
    wrongRoleRedirect: string;
};

export function useTicketDetail({
    ticketId,
    expectedRole,
    wrongRoleRedirect,
}: UseTicketDetailOptions) {
    const [ticket, setTicket] = useState<TicketDetail | null>(null);
    const [loadError, setLoadError] = useState("");
    const [isLoading, setIsLoading] = useState(true);

    const router = useRouter();

    useEffect(() => {
    async function loadTicket() {
        try {
            const data = await getCurrentUser();

            if (data.user.role !== expectedRole) {
                router.replace(wrongRoleRedirect);
                return;
            }

            const numericTicketId = Number(ticketId)

            if (Number.isNaN(numericTicketId)) {
                setLoadError("Invalid ticket id.");
                setIsLoading(false);
                return;
            }

            const ticketData = await getTicket(numericTicketId);
            setTicket(ticketData.ticket);
            setIsLoading(false);
        } catch {
            setLoadError("Failed to load ticket.");
            setIsLoading(false);
        }
    }

    loadTicket();
}, [ticketId, expectedRole, wrongRoleRedirect, router]);

return {
    ticket,
    setTicket,
    loadError,
    isLoading,
};
}

