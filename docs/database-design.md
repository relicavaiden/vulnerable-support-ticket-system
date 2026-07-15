# Database Design

## Purpose

The purpose of the database is to store the core data needed by the backend for the Vulnerable Support Ticket System.

The database will store users, tickets, ticket notes, ticket ownership, ticket assignment, and basic ticket status information. The backend will use this data to determine what information should be returned to the frontend and what actions each authenticated user is allowed to perform.

The database should support the Version 1 workflow while remaining simple enough to understand, test, and later secure.

## Users Table

The `users` table stores seeded user accounts for Version 1.

Planned fields:

* `id`
* `username`
* `password_hash`
* `role`
* `is_seeded`
* `created_at`

The `role` field will determine whether a user is a `requester` or a `resolver`.

Public user registration is out of scope for Version 1, so users will be manually seeded.

## Tickets Table

The `tickets` table stores the main support ticket records.

Planned fields:

* `id`
* `title`
* `description`
* `status`
* `category`
* `requester_id`
* `assigned_resolver_id`
* `created_at`
* `updated_at`

The `requester_id` field connects the ticket to the user who created it.

The `assigned_resolver_id` field connects the ticket to the resolver responsible for working on it.

Version 1 ticket statuses:

* `open`
* `in_progress`
* `resolved`

## Ticket Notes Table

The `ticket_notes` table stores notes and updates added to a ticket.

Planned fields:

* `id`
* `ticket_id`
* `author_id`
* `note_type`
* `body`
* `created_at`

The `ticket_id` field connects the note to a specific ticket.

The `author_id` field connects the note to the user who created it.

The `note_type` field identifies the type of note, such as `requester_note`, `resolver_note`, or `status_update`.

In Version 1, ticket notes will use `note_type` to identify whether a note was created by a requester, resolver, or system workflow.

A future version may add a `visibility` field to distinguish between public ticket updates and internal resolver-only notes.

## Relationships

The planned relationships are:

* `tickets.requester_id` references `users.id`
* `tickets.assigned_resolver_id` references `users.id`
* `ticket_notes.ticket_id` references `tickets.id`
* `ticket_notes.author_id` references `users.id`

These relationships allow the backend to determine ticket ownership, ticket assignment, and note authorship.

## Authorization Impact

The database design supports backend authorization checks.

For ticket access, the backend should check the logged-in user's relationship to the ticket.

A requester should only be able to access tickets where:

* `tickets.requester_id` matches the logged-in user's ID

A resolver should only be able to access tickets where:

* `tickets.assigned_resolver_id` matches the logged-in user's ID

Ticket status should not determine whether a user can view a ticket. A resolved ticket should remain protected unless the logged-in user is authorized to access it.

For ticket notes, the backend should first verify that the logged-in user is allowed to access the ticket. After that, the backend can determine which notes should be returned based on the user's role and the note behavior defined by the application.

For Version 1, all notes attached to a ticket are visible only to users who are authorized to view that ticket.

This means:

* The requester can see notes on their own ticket.
* The assigned resolver can see notes on that assigned ticket.
* Other requesters cannot see the ticket or its notes.
* Other resolvers cannot see the ticket or its notes.

A future version may separate note visibility into public and internal notes.

Example future behavior:

* Public notes are visible to the requester, assigned resolver, and admin.
* Internal notes are visible only to the assigned resolver and admin.

## Deferred Fields

The following fields or concepts are deferred until later versions:

* Admin role behavior
* Admin dashboard fields
* Ticket deletion fields
* Soft-delete tracking
* Ticket search indexes
* File attachment metadata
* Email notification fields
* Password reset fields
* Advanced unread-note tracking
* Audit logging fields
* Note visibility, such as `public` or `internal`

A future `visibility` field may be added to ticket notes to separate requester-visible updates from resolver-only internal notes.

Admins should eventually be represented as users with an `admin` role instead of requiring a separate admin table.
