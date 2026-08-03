
const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:5000";

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
        body: JSON.stringify({ username, password}),
    });

    if (!response.ok) {
        throw new Error("Invalid username or password");
    }

    return response.json()
}

export async function getCurrentUser(): Promise<AuthResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
        method: "GET",
        credentials: "include",
    });

    if (!response.ok) {
        throw new Error("Not authenticated");
    }

    return response.json()
}

export async function logout(): Promise<MessageResponse> {
    const response = await fetch(`${API_BASE_URL}/api/auth/logout`,{
        method: "POST",
        credentials: "include",
    });

    if (!response.ok) {
        throw new Error("Logout failed");
    }

    return response.json();
}