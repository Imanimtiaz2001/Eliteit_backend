# User Subscription Management System - Backend

## Overview
This repository contains the backend code for the **User Subscription Management System**, built using **Flask**. The system enables secure user authentication, subscription management, and profile updates. It communicates with the frontend (Flutter) via REST API endpoints and handles business logic for user registration, login, profile management, and subscription management.

## Features
- **User Authentication**: Handles user login, registration, and token generation with JWT (JSON Web Tokens).
- **Subscription Management**: Allows users to subscribe to different plans (Basic, Premium) and manages subscription statuses.
- **Profile Management**: Users can view and update their profile details, including name, address, and subscription status.
- **Admin Panel**: Admin users can view expired subscriptions and manage them.
- **Automated Tasks**: Cron jobs update expired subscriptions automatically.

## Project Setup

### Prerequisites
- Python 3.x
- Flask 3.x
- MySQL (or any other compatible database)
- JWT for authentication
- Cron jobs for automated tasks

### Installation

1. **Clone the repository**:
    ```bash
    git clone https://github.com/ImanImtiaz2001/Eliteit_backend.git
    cd Eliteit_backend
    ```

2. **Create and activate a virtual environment**:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install dependencies**:
    The project uses `requirements.txt` to manage dependencies. Run the following command to install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. **Setup Environment Variables**:
    Create a `.env` file in the root directory with the following configurations:
    ```env
    JWT_SECRET_KEY=your_secret_key
    DATABASE_URI=mysql://username:password@localhost/database_name
    ```

5. **Run the application**:
    Start the Flask application by running:
    ```bash
    python app.py
    ```
    The application will run locally on `http://127.0.0.1:5000`.

### Folder Structure
/app /models # Database models (User, Subscription) /routes # API routes for user and subscription management /utils # Utility functions (JWT handling, database setup) /services # Business logic for handling subscriptions, user registration, etc. /config # Configuration files config.py # Configurations for the app (e.g., JWT_SECRET_KEY) /migrations # Database migrations /versions # Generated migration scripts


### Models
The application uses **SQLAlchemy** for database management. The following models are defined:
- **User**: Stores user information such as email, password, profile information.
- **Subscription**: Stores subscription details like plan type, start date, end date, and status.

### API Endpoints
The backend exposes several REST API endpoints to handle user and subscription management. These endpoints are used by the Flutter frontend for user interactions.

1. **/register** (POST):
    - Registers a new user by accepting email, password, and confirm_password.
    - Hashes the password and stores it securely in the database.

2. **/login** (POST):
    - Authenticates a user with email and password.
    - Returns an access token and refresh token on successful authentication.

3. **/refresh** (POST):
    - Refreshes the access token using a valid refresh token.

4. **/subscribe** (POST):
    - Allows authenticated users to subscribe to a plan (Basic, Premium, Enterprise).
    - Ensures users cannot have multiple active subscriptions at once.

5. **/profile** (GET):
    - Fetches the user's profile data (name, email, active subscription status).

6. **/update-profile** (PUT):
    - Allows users to update their profile information (name, address, etc.).

7. **/admin** (GET):
    - Admin endpoint to fetch expired subscriptions and manage them.

### Background Jobs (Cron Jobs)
- **update_inactive_subscriptions.py**: Runs as a scheduled job (via cron) to deactivate subscriptions that have expired.

### Testing
Testing is conducted to ensure the reliability of the backend services:
- **Backend Tests**: Use Postman to test endpoints like `/register`, `/login`, `/subscribe`, and `/profile`.
- **Profile Update Tests**: Ensure the `/update-profile` endpoint correctly handles user profile data.

### Code Management and GitHub

- **Version Control**: The project is managed with Git and hosted on GitHub.
- **Branching Strategy**: Use `main` for production-ready code and `develop` for active development.
- **Commit Guidelines**: Regular commits with clear, descriptive messages for every new feature or fix.

### Deployment

#### Local Execution

1. **Backend**: To run the backend locally, ensure the Flask app is running:
    ```bash
    python app.py
    ```
    The app will be available at `http://127.0.0.1:5000`.

2. **Database Setup**: Run migrations to set up the database:
    ```bash
    flask db init
    flask db migrate
    flask db upgrade
    ```

#### Deployment with Docker
To deploy the application using Docker:

1. **Build the Docker image**:
    ```bash
    docker build --no-cache -t eliteit_backend .
    ```

2. **Run the container**:
    ```bash
    docker run -p 5000:5000 --env-file .env eliteit_backend
    ```

### Dependencies

The project relies on the following packages:
- Flask==3.1.0
- Flask-JWT-Extended==4.7.1
- Flask-SQLAlchemy==3.1.1
- Flask-Cors==5.0.1
- python-dotenv==1.1.0
- SQLAlchemy==2.0.40
- PyJWT==2.10.1

You can install these dependencies by running:
```bash
pip install -r requirements.txt

**### Conclusion**
The User Subscription Management System backend is built with Flask, providing secure authentication, subscription management, and profile management. The backend efficiently interacts with the frontend and handles all business logic related to user interactions. The system also uses cron jobs for automated subscription expiration updates and ensures that only authorized users (admin) can view expired subscriptions.


---

For more information, please refer to the [Frontend Documentation](https://github.com/ImanImtiaz2001/Subscriptionsystem_Frontend).

