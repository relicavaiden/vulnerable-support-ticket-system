import RoleGuard from "@/components/auth/RoleGuard";
import AppShell from "@/components/layout/AppShell";

export default function RequesterLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <RoleGuard
            expectedRole="requester"
            wrongRoleRedirect="/resolver/tickets"
            >
            <AppShell roleLabel="Requester">
                {children}
            </AppShell>
        </RoleGuard>
    );
}