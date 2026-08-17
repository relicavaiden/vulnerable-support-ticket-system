import AppShell from "@/components/layout/AppShell";

export default function RequesterLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <AppShell roleLabel="Requester">
            {children}
        </AppShell>
    );
}