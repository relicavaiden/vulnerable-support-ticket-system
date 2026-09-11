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
    const router = useRouter()
    const [ticket, setTicket] = useState<TicketDetail | null>(null);
    const [loadError, setLoadError] = useState("");
    const [isLoading, setIsLoading] = useState(true);
    const [loadedRequestKey, setLoadedRequestKey] = useState<string | null>(null);

    const requestKey = `${expectedRole}:${ticketId}`;

    useEffect(() => {
        async function loadTicket() {
            setIsLoading(true);
            setTicket(null);
            setLoadError("");
            setLoadedRequestKey(null);

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
            setLoadedRequestKey(requestKey);
            setIsLoading(false);
        } catch {
            setLoadError("Failed to load ticket.");
            setIsLoading(false);
        }
    }

    loadTicket();
}, [ticketId, expectedRole, wrongRoleRedirect, router]);

const isCurrentRequestLoaded = loadedRequestKey === requestKey;

return {
    ticket,
    setTicket,
    loadError,
    isLoading,
    isCurrentRequestLoaded,
};
}

