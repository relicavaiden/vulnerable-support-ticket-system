"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { getCurrentUser } from "@/lib/api";

type RoleGuardProps = {
    expectedRole: "requester" | "resolver";
    wrongRoleRedirect: string;
    children: React.ReactNode;
};

export default function RoleGuard({
    expectedRole,
    wrongRoleRedirect,
    children,
}: RoleGuardProps) {
    const router = useRouter();

    const [isChecking, setIsChecking] = useState(true);
    const [isAuthorized, setIsAuthorized] = useState(false);

    useEffect(() => {
    async function checkAuthorization() {
        try {
            // 1. getCurrentUser()
            const data = await getCurrentUser();

            // 2. compare data.user.role with expectedRole
            if (data.user.role !== expectedRole) {
                    router.replace(wrongRoleRedirect);
                    return;
                }

            setIsAuthorized(true);

        } catch {
            router.replace("/login");
        }
    }

    checkAuthorization();
}, [expectedRole, wrongRoleRedirect, router]);

if (!isAuthorized) {
                return null;
            }

            return children;
        }