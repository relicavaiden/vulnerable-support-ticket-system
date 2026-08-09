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

export type TicketCategory =
    | "account_access"
    | "hardware"
    | "software"
    | "network"
    | "other";

export type TicketStatus = 
    | "open"
    | "in_progress"
    | "resolved";

export type Ticket = {
    id: number;
    title: string;
    description: string;
    status: TicketStatus;
    category: TicketCategory;
};

type TicketsResponse = {
    tickets: Ticket[];
};

type CreateTicketRequest = {
    title: string;
    description: string;
    category: TicketCategory;
};

type CreateTicketResponse = {
    ticket: Ticket;
};

export type TicketNote = {
    id: number;
    ticket_id: number;
    author_id: number;
    author_username: string;
    note_type: "requester_note" | "resolver_note" | "status_update";
    body: string;
    created_at: string;
};

export type TicketDetail = Ticket & {
    notes: TicketNote[];
};

type TicketDetailResponse = {
    ticket: TicketDetail;
};

type CreateTicketNoteRequest = {
    body: string;
};

type CreateTicketNoteResponse = {
    note: TicketNote;
};

type UpdateTicketStatusRequest = {
    status: TicketStatus; 
};

type UpdateTicketStatusResponse = {
    ticket: {
        id: number;
        status: TicketStatus;
    };
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

export async function getTicket(
    ticketId: number
): Promise<TicketDetailResponse> {
    const response = await fetch(`${API_BASE_URL}/api/tickets/${ticketId}`, {
        method: "GET",
        credentials: "include",
    });

    if (!response.ok) {
        throw new Error("Failed to load ticket");
    }

    return response.json();
}

export async function addTicketNote(
    ticketId: number,
    noteData: CreateTicketNoteRequest
): Promise<CreateTicketNoteResponse> {
    const response = await fetch(`${API_BASE_URL}/api/tickets/${ticketId}/notes`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(noteData),
    });

    if (!response.ok) {
        throw new Error("Failed to add note");
    }

    return response.json();
}

export async function updateTicketStatus(
    ticketId: number,
    statusData: UpdateTicketStatusRequest
): Promise<UpdateTicketStatusResponse> {
    const response = await fetch(`${API_BASE_URL}/api/tickets/${ticketId}/status`,
        {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify(statusData),
        }
    );

    if (!response.ok) {
        throw new Error("Failed to update ticket status");
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