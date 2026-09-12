# Vulnerable Support Ticket System

## Project Overview

The Vulnerable Support Ticket System (VSTS) is a full-stack support ticket application built to demonstrate secure software development, backend engineering, authentication, authorization, vulnerability research, and security remediation.

The project was intentionally developed in phases:

- **V1 — Vulnerable Baseline:** Build a functioning support ticket application while preserving intentionally weak security behavior for controlled testing.
- **V2 — Security Remediation:** Reproduce security weaknesses, identify trust boundaries, implement remediations, and verify those remediations through automated and manual testing.
- **V3 — Planned:** Production identity, administration, session management, audit capabilities, and additional operational controls.
- **V4 — Future:** Infrastructure observability, logging, monitoring, and defensive operations.

The intentionally vulnerable V1 build is preserved separately for local vulnerability reproduction and evidence capture.

The public deployment runs the remediated V2 application.

---

## Live Demo

The remediated V2 application is deployed at:

**https://vsts.relicavaiden.com**

### Demo Accounts

#### Requester

- Username: `requester_demo`
- Password: `requester123`

#### Resolver

- Username: `resolver_demo`
- Password: `resolver123`

These accounts are seeded specifically for public demonstration and testing.

> The intentionally vulnerable V1 build is not publicly deployed.

### What to Test

- Requester ticket creation
- Requester follow-up notes
- Resolver notes
- Resolver ticket status updates
- Requester/resolver authorization boundaries
- Session-based authentication
- Logout and session revocation behavior

The public demo uses non-privileged seeded accounts only. No administrative credentials or production secrets are exposed.

---

## Tech Stack

### Frontend

- Next.js 16
- React
- TypeScript
- Tailwind CSS

### Backend

- Flask
- Python
- Gunicorn

### Database

- SQLite

### Testing

- Pytest
- Flask test client
- Manual browser and API verification

### Deployment

- AWS EC2
- Ubuntu Linux
- Nginx reverse proxy
- Gunicorn WSGI server
- systemd-managed frontend and backend services
- Elastic IP
- Let's Encrypt TLS certificate
- Custom domain: `vsts.relicavaiden.com`

---

## Application Architecture

```text
Browser
   |
   | HTTPS
   v
Nginx
   |
   |-- / --------> Next.js :3000
   |
   `-- /api/* ---> Gunicorn :5001
                         |
                         v
                       Flask
                         |
                         v
                       SQLite

Nginx provides the public HTTP/HTTPS boundary while the Next.js and Flask services remain bound to localhost on the EC2 instance.

The Flask application trusts one reverse-proxy hop in production so that the application can correctly interpret the originating client IP while avoiding unrestricted trust of forwarded headers.

⸻

Core Application Features

Requester

* Login
* View owned tickets
* Create tickets
* View ticket details
* Add follow-up notes

Resolver

* Login
* View assigned tickets
* View ticket details
* Add resolver notes
* Update ticket status

Shared Behavior

* Seeded demo users
* Backend-derived user identity
* Role-based access control
* Server-side session validation
* Ticket ownership and assignment enforcement
* Session revocation on logout
* Absolute session expiration
* Authentication rate limiting

⸻

Security Model

The frontend does not determine ownership or authoritative identity.

Requester and resolver identities are derived from the authenticated backend session.

Requester Boundary

A requester may access only tickets that belong to that requester.

Resolver Boundary

A resolver may access only tickets assigned to that resolver.

Authentication

Successful authentication creates:

* A signed Flask session
* A server-side session record stored in SQLite

The browser session stores identifiers used to locate and validate the corresponding server-side session.

Protected backend routes verify that:

* The user ID exists
* The session ID exists
* The server-side session exists
* The session has not been revoked
* The session belongs to the authenticated user
* The session has not exceeded its maximum lifetime

⸻

Confirmed Security Findings

V2 security work followed a basic process:

Hypothesis
    ↓
Reproduction
    ↓
Evidence
    ↓
Classification
    ↓
Remediation
    ↓
Verification

Not every suspicious behavior was classified as a vulnerability. Findings were promoted only when the behavior could be reproduced and the security impact could be demonstrated.

VULN-001 — Weak / Default Flask Signing Secret

V1 used a known development signing secret.

A legitimate session cookie could be decoded, modified, re-signed, and accepted by the application.

This demonstrated that signed-cookie integrity depends on the secrecy of the signing key.

Remediation

* Removed the fallback signing secret
* Require SECRET_KEY from the deployment environment
* Application startup fails closed if no secret is configured
* Historical V1 cookies are not accepted by the V2 deployment

⸻

VULN-002 — Unrestricted Authentication Attempts

V1 allowed repeated authentication attempts without throttling.

Repeated incorrect passwords could be submitted and a correct password could immediately be attempted afterward.

Remediation

V2 implements SQLite-backed authentication rate limiting.

Two scopes are used:

IP + Username

* 5 failed attempts within 60 seconds
* 60-second cooldown

IP-Wide

* 20 total login requests within 60 seconds
* 60-second cooldown

Unknown usernames participate in rate limiting so that account existence is not required for the control to apply.

⸻

VULN-003 — Logged-Out Session Replay

In the vulnerable implementation, logging out removed the browser’s current session cookie but did not provide server-side revocation.

A previously copied valid cookie could therefore be replayed after logout.

Remediation

V2 introduced server-side session tracking.

* Login creates a random server-side session ID
* Session records are stored in SQLite
* Logout revokes the server-side session before clearing the browser session
* Protected routes validate the server-side session
* Replaying a revoked cookie results in an authentication failure

⸻

VULN-004 — No Application-Enforced Session Expiration

A valid server-side session could continue to be accepted because session age was recorded but was not part of the authentication decision.

Remediation

V2 enforces a four-hour absolute session lifetime.

Expired sessions are rejected by the same shared authentication guard used by protected backend routes.

⸻

Positive Security Controls

Several security hypotheses were tested but were not reproduced as exploitable vulnerabilities.

Broken Object Level Authorization / IDOR

Requester ownership and resolver assignment boundaries held during testing.

Unauthorized ticket access returned 403 and did not mutate protected resources.

SQL Injection

SQL-shaped input remained data.

Database queries use parameterized SQL and route parameters enforce expected ticket ID formats.

SQL injection was not reproduced.

Stored Cross-Site Scripting

Script-shaped content could be stored as ticket data, but React rendered it as text.

No unsafe HTML rendering path such as dangerouslySetInnerHTML was used.

Stored XSS was not reproduced.

CORS

Untrusted origins did not receive credentialed CORS permission.

Trusted development origins received the expected headers.

Permissive credentialed CORS was not reproduced.

Error Disclosure

Malformed and unexpected input was tested for stack traces, filesystem paths, SQLite information, and debugger output.

The production API returned controlled responses.

Production error disclosure was not reproduced.

CSRF

Classic form-based cross-site requests were tested against the JSON API.

The tested attack path was not reproduced due to the combination of JSON handling, cookie behavior, and CORS restrictions.

No practical classic-form CSRF vulnerability was confirmed during V2.

⸻

Session and Cookie Configuration

The deployed V2 application uses:

* HttpOnly=True
* Secure=True
* SameSite=Lax
* Server-side session revocation
* Four-hour absolute session lifetime
* HTTPS-only public deployment

The application is deployed behind Nginx and explicitly trusts one reverse-proxy hop.

⸻

Testing Strategy

The project includes tests covering:

* Authentication
* Authorization
* Ticket ownership
* Resolver assignment
* Session creation
* Session ownership
* Session revocation
* Session expiration
* Login rate limiting
* Rate-limit reset behavior
* Rate-limit isolation
* SQL injection hypotheses
* Stored XSS hypotheses
* CORS behavior
* Error disclosure behavior

A passing test is treated as evidence only when the test actually establishes the intended security claim.

⸻

V1

V1 established the functional baseline for the application.

Features included:

* Seeded requester and resolver users
* Login
* Ticket creation
* Ticket detail views
* Requester notes
* Resolver notes
* Ticket status updates
* Automatic assignment to a seeded resolver

The frozen V1 version is preserved as:

v1.0.0

V1 is used locally for vulnerability reproduction and evidence capture and is intentionally not exposed to the public internet.

⸻

V2

V2 converted the project from a functioning support application into a security testing and remediation environment.

V2 includes:

* Security hypothesis testing
* Vulnerability reproduction
* Authentication hardening
* Rate limiting
* Server-side session management
* Session revocation
* Session expiration
* Shared authentication guards
* Authorization verification
* Positive security controls
* Automated security-focused tests
* Production deployment

The completed V2 baseline is preserved as:

v2.0.0

The remediated V2 application is currently deployed at:

https://vsts.relicavaiden.com

⸻

Planned V3 Scope

V3 will focus on production identity and administration rather than repeating the V2 remediation process.

Potential areas include:

* OIDC / OAuth integration
* MFA for privileged users
* Account recovery
* Session history
* Idle-session controls
* Session rotation
* Concurrent session management
* Administrative session termination
* Admin role management
* Resolver assignment
* Access reviews
* Privileged activity auditing
* Authentication audit events
* Consent-aware telemetry
* Data minimization
* Retention and privacy controls

V3 is intentionally deferred while V2 is documented and presented.

⸻

Future Infrastructure Work

Future infrastructure work may include:

* Centralized logging
* Monitoring
* Security event aggregation
* SIEM integration
* Database migration strategy
* Automated demo-data cleanup
* Backup and recovery improvements
* Deployment automation
* Additional observability

⸻

Project Status

V1

Complete and frozen

V2

Complete, deployed, and production-verified

V3

Planned

Current Focus

* Vulnerability reproduction recordings
* Remediation evidence
* Security documentation
* Portfolio integration
* Technical blog articles

⸻

Disclaimer

This project contains intentionally vulnerable historical code for educational and portfolio purposes.

The vulnerable V1 environment is maintained locally and is not publicly deployed.

The public application at vsts.relicavaiden.com runs the remediated V2 implementation.