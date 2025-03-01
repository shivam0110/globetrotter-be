# Globetrotter Backend

This is the backend API for the Globetrotter geography quiz game, built with Flask and Prisma.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Generate Prisma client:
   ```
   prisma generate
   ```

3. Run the application:
   ```
   python main.py
   ```

4. Seed the database (optional):
   ```
   curl -X POST http://localhost:8000/api/seed-database
   ```

## API Endpoints

- `GET /api/destinations/random` - Get a random destination with clues
- `GET /api/destinations/options?destination_id=1` - Get multiple choice options
- `POST /api/destinations/check-answer` - Verify user answers
- `POST /api/users` - Create a new user
- `GET /api/users/{username}` - Get user details
- `POST /api/users/challenge` - Create a challenge session
- `GET /api/users/challenge/{invite_code}` - Get challenge details 