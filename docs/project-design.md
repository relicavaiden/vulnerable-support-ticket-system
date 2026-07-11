# Vulnerable Support Ticket System - Project Design

## Project Purpose

This project is an intentionally vulnerable support ticket system built to demonstrate secure software development, OWASP Top 10 concepts, backend engineering, authentication, authorization, and security remediation.

The application will first be built with intentionally vulnerable patterns. Later, those vulnerabilities will be identified, exploited in a controlled environment, remediated, tested, and documented as part of a professional cybersecurity and software engineering portfolio project.

The goal is not only to build a working application, but to understand how real security weaknesses are introduced into software systems and how secure design decisions prevent them.

## Version 1 Scope

Version 1 will focus on a basic support ticket workflow using manually seeded users.

Planned V1 features include:

* Seeded requester and resolver users
* User login
* Ticket creation
* Ticket detail view
* Requester follow-up notes
* Resolver notes
* Ticket status updates
* Automatic ticket assignment to a seeded resolver

Version 1 will prioritize a small, understandable system over a large feature set.

## Tech Stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

### Backend

* Flask
* Python

### Database

* SQLite

### Deployment

* AWS deployment is planned for a later phase.

## User Roles

### Requester

A requester represents a user who creates support tickets.

Requesters can:

* Log in
* Create tickets
* View their own tickets
* View details for their own tickets
* Add follow-up notes to their own tickets

Requesters cannot:

* View tickets created by other requesters
* View all tickets in the system
* Change ticket status
* Add resolver-only notes
* Assign tickets
* Delete tickets

### Resolver

A resolver represents a user responsible for working assigned tickets.

Resolvers can:

* Log in
* View tickets assigned to them
* View details for assigned tickets
* Add resolver notes
* Change ticket status

Resolvers cannot:

* View tickets not assigned to them
* View all tickets in the system
* Delete tickets
* Manage users
* Assign tickets in Version 1

### Admin

The admin role is planned for a future version.

Admin functionality is intentionally out of scope for Version 1 to keep the first implementation focused on authentication, authorization, ticket creation, ticket viewing, and ticket updates.

## Ticket Statuses

Version 1 will support the following ticket statuses:

* `open`
* `in_progress`
* `resolved`

Future versions may include:

* `closed`
* `reopened`
* `researching`
* `reviewing`

Additional statuses are deferred because each status introduces new workflow rules, permissions, and edge cases.

## Core Workflows

### Requester Workflow

1. A requester logs in.
2. The requester creates a new ticket.
3. The ticket is automatically assigned to a seeded resolver.
4. The requester can view their own ticket.
5. The requester can add follow-up notes after the ticket has been created.

### Resolver Workflow

1. A resolver logs in.
2. The resolver views tickets assigned to them.
3. The resolver opens a ticket detail view.
4. The resolver adds notes to the ticket.
5. The resolver updates the ticket status.

## Authorization Rules

The backend must enforce authorization rules. The frontend may hide or show interface elements, but frontend behavior should not be trusted as a security control.

Version 1 authorization rules:

1. A requester can only view tickets they created.
2. A requester can only add follow-up notes to tickets they created.
3. A requester cannot change ticket status.
4. A resolver can only view tickets assigned to them.
5. A resolver can only add resolver notes to tickets assigned to them.
6. A resolver can only update the status of tickets assigned to them.
7. Tickets are automatically assigned to a seeded resolver in Version 1.
8. Tickets cannot be deleted in Version 1.
9. Admin functionality is not implemented in Version 1.

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
* Multi-resolver assignment
* Production AWS deployment

These features may be added later if they support a specific engineering or security learning objective.

## Planned Vulnerabilities

This project will intentionally demonstrate several common web application vulnerabilities.

Planned vulnerability areas include:

* Broken Access Control
* SQL Injection
* Stored Cross-Site Scripting
* Weak authentication or session handling
* Security misconfiguration

Each vulnerability should be documented with:

* The vulnerable behavior
* The affected route or feature
* The security principle being violated
* A controlled proof of concept
* The potential real-world impact
* The secure remediation

## Future Secure Remediation

After the vulnerable implementation is complete, the application will be secured and documented.

Future remediation work may include:

* Enforcing backend authorization checks
* Using parameterized SQL queries
* Escaping or sanitizing user-controlled output
* Improving authentication and session handling
* Adding stronger validation
* Improving error handling
* Removing insecure debug behavior
* Adding tests for security regressions
* Updating documentation with before-and-after comparisons

## Project Status

Planning phase.
