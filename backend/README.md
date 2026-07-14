# Backend

This folder will contain the Flask API for the Vulnerable Support Ticket System.

The backend is responsible for authentication, authorization, ticket business logic, database access, and API responses.

## Running the Backend Locally

From the 'backend/' directory:

'''bash
source .venv/bin/activate
flask --app app run

http://127.0.0.1:5000/api/health