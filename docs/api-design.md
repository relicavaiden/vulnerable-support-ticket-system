# API Design

## Purpose

This document defines the initial API contract between the Next.js frontend and Flask backend for the Vulnerable Support Ticket System.

The application will be built as an intentionally vulnerable support ticket system that demonstrates OWASP Top 10 vulnerabilities, backend engineering concepts, authentication, authorization, and later security remediation.

The API should define what the frontend can request, what the backend is responsible for enforcing, and where the trust boundaries exist between the client, server, and database.

## Authentication Routes

Version 1 will use manually seeded users instead of public registration.

Planned authentication routes:

| Method | Route              | Purpose                                 |
| ------ | ------------------ | --------------------------------------- |
| `POST` | `/api/auth/login`  | Authenticate a seeded user              |
| `POST` | `/api/auth/logout` | Log out the current user                |
| `GET`  | `/api/auth/me`     | Return the currently authenticated user |

The login route should accept user credentials and create an authenticated session.

The frontend should not decide the user's role. After login, the backend should return the authenticated user's safe user context, such as username and role.

## User Context

Users will have roles that determine what actions they are allowed to perform.

Version 1 roles:

| Role        | Purpose                                                                |
| ----------- | ---------------------------------------------------------------------- |
| `requester` | Creates tickets and adds follow-up notes                               |
| `resolver`  | Works assigned tickets, adds resolver notes, and updates ticket status |

The `admin` role is planned for a future version and is out of scope for Version 1.

The frontend may use the user's role to display the correct interface, but the backend must enforce all role-based permissions.

## Ticket Routes

Planned ticket routes:

| Method  | Route                           | Purpose                                                     |
| ------- | ------------------------------- | ----------------------------------------------------------- |
| `GET`   | `/api/tickets`                  | Return tickets visible to the logged-in user                |
| `POST`  | `/api/tickets`                  | Create a new ticket as a requester                          |
| `GET`   | `/api/tickets/:ticketId`        | Return one visible ticket with its notes                    |
| `PATCH` | `/api/tickets/:ticketId/status` | Allow a resolver to update the status of an assigned ticket |

For requesters, `GET /api/tickets` should return only tickets created by the logged-in requester.

For resolvers, `GET /api/tickets` should return only tickets assigned to the logged-in resolver.

The frontend should not send `requester_id` or `resolver_id` when creating or updating tickets. The backend should determine ownership and assignment based on the authenticated session and server-side rules.

## Note Behavior

Ticket notes should be returned with the ticket detail response in Version 1.

This means:

| Method | Route                          | Purpose                        |
| ------ | ------------------------------ | ------------------------------ |
| `POST` | `/api/tickets/:ticketId/notes` | Add a note to a visible ticket |

Notes should be displayed in the order they were created.

Requesters can add follow-up notes to tickets they created.

Resolvers can add resolver notes to tickets assigned to them.

In Version 1, notes do not need a separate fetch endpoint because that would add unnecessary complexity before the core ticket workflow is complete.

## Ticket Statuses

Version 1 ticket statuses:

* `open`
* `in_progress`
* `resolved`

A resolved ticket should still only be visible to users who are authorized to view it.

Ticket status should not determine whether private ticket data becomes visible to other users.

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

## Frontend Trust Boundary

The frontend is responsible for displaying forms, buttons, pages, and ticket information to the user.

The frontend is not responsible for enforcing security.

A user can inspect frontend code, modify requests, change form values, or call API routes directly using browser developer tools or external tools.

Because of this, the backend must not trust client-provided role, requester ID, resolver ID, ownership, or assignment data.

The backend should determine the logged-in user from the authenticated session and apply authorization rules before returning or modifying ticket data.

## Out of Scope for Version 1

The following features are intentionally excluded from Version 1:

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
* Production AWS deployment

Basic `created_at` and `updated_at` timestamps may still be included because they are useful for debugging, ticket ordering, and future documentation.
