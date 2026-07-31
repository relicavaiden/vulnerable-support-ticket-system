# API Design

## Purpose

This document defines the Version 1 API contract between the Next.js frontend and Flask backend for the Vulnerable Support Ticket System.

The application is being built as an intentionally vulnerable support ticket system that demonstrates OWASP Top 10 vulnerabilities, backend engineering concepts, authentication, authorization, and later security remediation.

The API defines:

* What the frontend can request
* What the backend returns
* What the backend is responsible for enforcing
* Where the trust boundaries exist between the client, server, and database

The frontend may display different pages, buttons, and forms based on the logged-in user, but the backend must enforce all authentication and authorization rules.

## API Design Principles

Version 1 follows these principles:

* The frontend is not trusted to enforce security.
* The backend determines the logged-in user from the authenticated session.
* The backend determines the user's role from the database.
* The backend determines ticket ownership and assignment.
* The frontend should not send server-owned fields such as `requester_id`, `assigned_resolver_id`, `status`, or `note_type`.
* The backend must validate user input before saving it to the database.
* The backend must return safe user data and must not expose sensitive fields such as `password_hash`.

## Authentication Routes

Version 1 uses manually seeded users instead of public registration.

Version 1 authentication routes:

| Method | Route              | Purpose                                 |
| ------ | ------------------ | --------------------------------------- |
| `POST` | `/api/auth/login`  | Authenticate a seeded user              |
| `POST` | `/api/auth/logout` | Log out the current user                |
| `GET`  | `/api/auth/me`     | Return the currently authenticated user |

### POST /api/auth/login

Authenticates a seeded user and creates an authenticated session.

#### Request Body

```json
{
  "username": "requester_demo",
  "password": "requester123"
}
```

#### Success Response

The backend returns safe user context:

```json
{
  "user": {
    "id": 1,
    "username": "requester_demo",
    "role": "requester"
  }
}
```

The login response must not include sensitive fields such as `password_hash`.

If the username or password is invalid, the API returns `401`.

The frontend should not decide the user's role. After login, the frontend may use the returned role to display the correct interface, but the backend must still enforce all role-based permissions.

### GET /api/auth/me

Returns the currently authenticated user based on the active session.

#### Success Response

```json
{
  "user": {
    "id": 1,
    "username": "requester_demo",
    "role": "requester"
  }
}
```

If there is no active authenticated session, the API returns `401`.

If the session references a user that no longer exists, the API returns `401`.

### POST /api/auth/logout

Clears the authenticated session.

#### Success Response

```json
{
  "message": "Logged out successfully"
}
```

## User Context

Users have roles that determine what actions they are allowed to perform.

Version 1 roles:

| Role        | Purpose                                                                |
| ----------- | ---------------------------------------------------------------------- |
| `requester` | Creates tickets and adds follow-up notes                               |
| `resolver`  | Works assigned tickets, adds resolver notes, and updates ticket status |

The `admin` role is planned for a future version and is out of scope for Version 1.

The frontend may use the user's role to display the correct interface, but the backend must enforce all role-based permissions.

## Ticket Routes

Version 1 ticket routes:

| Method  | Route                           | Purpose                                            |
| ------- | ------------------------------- | -------------------------------------------------- |
| `GET`   | `/api/tickets`                  | Return tickets visible to the logged-in user       |
| `POST`  | `/api/tickets`                  | Create a new ticket as a requester                 |
| `GET`   | `/api/tickets/:ticketId`        | Return one visible ticket with its notes           |
| `POST`  | `/api/tickets/:ticketId/notes`  | Add a note to a visible ticket                     |
| `PATCH` | `/api/tickets/:ticketId/status` | Allow an assigned resolver to update ticket status |

## GET /api/tickets

Returns tickets visible to the logged-in user.

For requesters, the API returns only tickets created by the logged-in requester.

For resolvers, the API returns only tickets assigned to the logged-in resolver.

If the user is not authenticated, the API returns `401`.

#### Success Response

```json
{
  "tickets": [
    {
      "id": 1,
      "title": "Cannot access account",
      "description": "User cannot log in.",
      "status": "open",
      "category": "account_access"
    }
  ]
}
```

## POST /api/tickets

Creates a new ticket as the authenticated requester.

Only users with the `requester` role can create tickets.

In Version 1, newly created tickets are automatically assigned to the seeded resolver.

The frontend should not send `requester_id`, `assigned_resolver_id`, or `status`.

The backend determines:

* `requester_id` from the authenticated session
* `assigned_resolver_id` from server-side assignment rules
* `status` as `open`

#### Request Body

```json
{
  "title": "Cannot access account",
  "description": "User cannot log in.",
  "category": "account_access"
}
```

#### Success Response

```json
{
  "ticket": {
    "id": 1,
    "title": "Cannot access account",
    "description": "User cannot log in.",
    "status": "open",
    "category": "account_access"
  }
}
```

If the user is not authenticated, the API returns `401`.

If the authenticated user is not a requester, the API returns `403`.

## GET /api/tickets/:ticketId

Returns one visible ticket with its notes.

The ticket must be visible to the logged-in user.

Requesters can view only tickets they created.

Resolvers can view only tickets assigned to them.

If the user is not authenticated, the API returns `401`.

If the ticket does not exist, the API returns `404`.

If the ticket exists but the logged-in user is not authorized to view it, the API returns `403`.

#### Success Response

```json
{
  "ticket": {
    "id": 1,
    "title": "Cannot access account",
    "description": "User cannot log in.",
    "status": "open",
    "category": "account_access",
    "notes": []
  }
}
```

The `notes` field is always returned as an array. If the ticket has no notes, the API returns an empty array.

## POST /api/tickets/:ticketId/notes

Adds a note to a visible ticket.

Requesters can add follow-up notes only to tickets they created.

Resolvers can add resolver notes only to tickets assigned to them.

The frontend should not send `note_type` or `author_id`.

The backend determines:

* `author_id` from the authenticated session
* `note_type` from the authenticated user's role

Role-based note types:

| Role        | Note Type        |
| ----------- | ---------------- |
| `requester` | `requester_note` |
| `resolver`  | `resolver_note`  |

#### Request Body

```json
{
  "body": "I still need help with this issue."
}
```

The note body is required.

If the body is missing, empty, or whitespace-only, the API returns `400`.

The backend trims leading and trailing whitespace from the note body before saving it.

#### Success Response

```json
{
  "note": {
    "id": 1,
    "ticket_id": 1,
    "author_id": 1,
    "note_type": "requester_note",
    "body": "I still need help with this issue.",
    "created_at": "2026-07-31 12:00:00"
  }
}
```

If the user is not authenticated, the API returns `401`.

If the ticket does not exist, the API returns `404`.

If the ticket exists but the logged-in user is not authorized to add a note to it, the API returns `403`.

## PATCH /api/tickets/:ticketId/status

Updates the status of an assigned ticket.

Only the resolver assigned to the ticket can update status.

Requesters cannot update ticket status.

The status field is required.

If the status is missing or invalid, the API returns `400`.

Allowed status values:

* `open`
* `in_progress`
* `resolved`

#### Request Body

```json
{
  "status": "in_progress"
}
```

#### Success Response

```json
{
  "ticket": {
    "id": 1,
    "status": "in_progress"
  }
}
```

When the status is updated, the backend creates a `ticket_notes` row with `note_type` set to `status_update`.

Example status update note body:

```txt
Status changed from open to in_progress.
```

If the user is not authenticated, the API returns `401`.

If the authenticated user is not a resolver, the API returns `403`.

If the ticket does not exist, the API returns `404`.

If a resolver attempts to update a ticket not assigned to them, the API returns `403`.

## Note Behavior

Ticket notes are returned with the ticket detail response in Version 1.

The `GET /api/tickets/:ticketId` route always returns a `notes` array. If the ticket has no notes, the API returns an empty array.

Notes are returned oldest-first using ascending note ID order.

Requesters can add follow-up notes to tickets they created.

Resolvers can add resolver notes to tickets assigned to them.

Status updates create system-style notes with `note_type` set to `status_update`.

In Version 1, notes do not need a separate fetch endpoint because notes are returned with the ticket detail response.

## Ticket Statuses

Version 1 ticket statuses:

* `open`
* `in_progress`
* `resolved`

A resolved ticket should still only be visible to users who are authorized to view it.

Ticket status should not determine whether private ticket data becomes visible to other users.

Future versions may add statuses such as:

* `closed`
* `reopened`
* `researching`
* `reviewing`

## Authorization Rules

The backend must enforce all authorization rules.

Version 1 authorization rules:

1. A requester can only view tickets they created.
2. A requester can only add notes to tickets they created.
3. A requester cannot update ticket status.
4. A resolver can only view tickets assigned to them.
5. A resolver can only add notes to tickets assigned to them.
6. A resolver can update the status only for tickets assigned to them.
7. A resolved ticket remains protected and should not become visible to all users.
8. The frontend should never be trusted to enforce access control.
9. Admin behavior is out of scope for Version 1.

The backend must distinguish between unauthenticated and unauthorized requests.

Unauthenticated users receive `401`.

Authenticated users who are not allowed to access a resource receive `403`.

## Frontend Trust Boundary

The frontend is responsible for displaying forms, buttons, pages, and ticket information to the user.

The frontend is not responsible for enforcing security.

A user can inspect frontend code, modify requests, change form values, or call API routes directly using browser developer tools or external tools.

Because of this, the backend must not trust client-provided role, requester ID, resolver ID, ownership, assignment, status, or note type data.

The backend should determine the logged-in user from the authenticated session and apply authorization rules before returning or modifying ticket data.

The frontend should not send:

* `role`
* `requester_id`
* `assigned_resolver_id`
* `author_id`
* `note_type`
* Initial ticket `status`

## Out of Scope for Version 1

The following API features are intentionally excluded from Version 1:

* Public user registration
* Admin dashboard
* Admin-created users
* Admin-based ticket assignment
* Ticket deletion
* Ticket search
* Viewing deleted tickets
* File attachments
* Email notifications
* Password reset
* Advanced unread-note tracking

Basic `created_at` and `updated_at` timestamps may still be included because they are useful for debugging, ticket ordering, and future documentation.

Production AWS deployment is planned for a future phase, but deployment details belong in the README or project design documentation rather than this API design document.
