"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getCurrentUser, getTickets } from "@/lib/api";

import type { Ticket, UserRole } from "@/lib/api";

type UseTicketListOptions = {
    expectedRole: UserRole;
    wrongRoleRedirect: string;
};

export function useTicketList({
    expectedRole, wrongRoleRedirect,
}: UseTicketListOptions) {
    const [tickets, setTickets] = useState<Ticket[]>([]);
    const [isLoading, setIsLoading] = useState(true);

    const router = useRouter();

    useEffect(() => {
        async function checkAuth() {
            try {
                const data = await getCurrentUser();

                if (data.user.role !== expectedRole) {
                    router.replace(wrongRoleRedirect);
                    return;
                }

                const ticketsData = await getTickets();

                setTickets(ticketsData.tickets);
                setIsLoading(false);
            } catch {
                router.replace("/login");
            }
        }
        checkAuth();
    }, [
        expectedRole,
        wrongRoleRedirect,
        router,
    ]);

    return {
        tickets,
        setTickets,
        isLoading,
    };
}