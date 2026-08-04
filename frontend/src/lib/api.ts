
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:5001";

type AuthResponse = {
    user: {
        id: number;
        username: string;
        role: "requester" | "resolver";
    };
};

type MessageResponse = {
    message: string;
};

export type Ticket = {
    id: number;
    title: string;
    description: string;
    status: "open" | "in_progress" | "resolved";
    category: string;
};

type TicketsResponse = {
    tickets: Ticket[];
};

type CreateTicketRequest = {
    title: string;
    description: string;
    category: string;
};

type CreateTicketResponse = {
    ticket: Ticket;
};

export async function login(
    username: string,
    password: string
): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
        throw new Error("Invalid username or password");
    }

    return response.json();
}

export async function getCurrentUser(): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        method: "GET",
        credentials: "include",
    });

    if (!response.ok) {
        throw new Error("Not authenticated");
    }

    return response.json();
}

export async function logout(): Promise<MessageResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/logout`, {
        method: "POST",
        credentials: "include",
    });

    if (!response.ok) {
        throw new Error("Logout failed");
    }

    return response.json();
}

export async function getTickets(): Promise<TicketsResponse> {
    const response = await fetch(`${API_BASE_URL}/api/tickets`, {
        method: "GET",
        credentials: "include",
    });

    if (!response.ok) {
        throw new Error("Failed to load tickets");
    }

    return response.json();
}

export async function createTicket(
    ticketData: CreateTicketRequest
): Promise<CreateTicketResponse> {
    const response = await fetch(`${API_BASE_URL}/api/tickets`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(ticketData),
    });

    if (!response.ok) {
        throw new Error("Failed to create ticket");
    }

    return response.json();
}