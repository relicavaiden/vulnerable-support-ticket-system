import LogoutButton from "../LogoutButton";

type AppShellProps = {
    roleLabel: string;
    children: React.ReactNode;
};

export default function AppShell({
    roleLabel,
    children,
}: AppShellProps) {
    return (
        <div className="min-h-screen bg-zinc-50">
            <header className="border-b bg-white">
                <div className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
                    <div>
                        <p className="text-sm text-zinc-500">Vulnerable Support Ticket System</p>

                        <p className="text-sm text-zinc-500">{roleLabel}</p>
                    </div>
                </div>

            <LogoutButton />
            </header>

            <main className="mx-auto w-full max-w-6xl px-6 py-8">
                {children}
            </main>
        </div>
    )
}