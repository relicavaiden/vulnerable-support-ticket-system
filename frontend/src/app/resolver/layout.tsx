import AppShell from "@/components/layout/AppShell";

export default function ResolverLayout({
    children,
}: Readonly<{
    children: React.ReactNode;
}>) {
    return (
        <AppShell roleLabel="Resolver">
            {children}
        </AppShell>
    );
}