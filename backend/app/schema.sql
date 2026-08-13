DROP TABLE IF EXISTS ticket_notes;
DROP TABLE IF EXISTS tickets;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('requester', 'resolver')),
    is_seeded INTEGER NOT NULL DEFAULT 0 CHECK (is_seeded IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tickets (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'resolved')),
    category TEXT NOT NULL CHECK (
        category IN (
            'account_access',
            'hardware',
            'software',
            'network',
            'other'
        )
    ),
    requester_id INTEGER NOT NULL,
    assigned_resolver_id INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (requester_id) REFERENCES users(id),
    FOREIGN KEY (assigned_resolver_id) REFERENCES users(id)
);

CREATE TABLE ticket_notes (
    id INTEGER PRIMARY KEY,
    ticket_id INTEGER NOT NULL, 
    author_id INTEGER NOT NULL,
    note_type TEXT NOT NULL CHECK (note_type IN ('requester_note', 'resolver_note', 'status_update')),
    body TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ticket_id) REFERENCES tickets(id),
    FOREIGN KEY (author_id) REFERENCES users(id)
);