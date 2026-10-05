# User Subscription Management System — Backend

Flask REST backend for a subscription-management application. The service provides authentication, profile management, subscription workflows, administrative views, and automated handling of expired subscriptions for a Flutter client.

## Features

- JWT-based user authentication.
- Registration and login.
- User profile management.
- Basic and Premium subscription plans.
- Subscription status management.
- Admin visibility into expired subscriptions.
- Automated expiration handling through scheduled jobs.

## API role

The backend acts as the service layer between the mobile client and the database.

## Technology

- Python
- Flask
- JWT authentication
- MySQL
- REST APIs
- Scheduled/cron-based tasks

## Local setup

1. Create a Python virtual environment.
2. Install the dependencies specified by the repository.
3. Configure database and authentication secrets through environment variables.
4. Initialize the database.
5. Start the Flask application.

Never commit real credentials, production database URLs, or populated secret files.

## Engineering focus

The project demonstrates a conventional backend service architecture with authentication, business logic, persistence, and scheduled state transitions.

## Related project

The Flutter client is maintained separately in Subscriptionsystem_Frontend.

## Future improvements

- Add automated unit and integration tests.
- Add OpenAPI documentation.
- Add stronger request validation and standardized error responses.
- Containerize the service and database for reproducible development.
- Add refresh-token rotation, rate limiting, and audit logging for production use.
