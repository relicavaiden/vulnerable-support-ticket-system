import RoleGuard from "@/components/auth/RoleGuard";
import AppShell from "@/components/layout/AppShell";

export default function ResolverLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <RoleGuard
            expectedRole="resolver"
            wrongRoleRedirect="/requester/tickets"
            >
            <AppShell roleLabel="Resolver">
                {children}
            </AppShell>
        </RoleGuard>
    );
}