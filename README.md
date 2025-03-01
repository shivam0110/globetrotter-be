# Globetrotter Backend

This is the backend API for the Globetrotter geography quiz game, built with Flask and Prisma.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file in the root directory
   - Add your PostgreSQL database URL:
     ```
     DATABASE_URL="postgresql://username:password@host:port/database"
     ```

3. Generate Prisma client:
   ```
   prisma generate
   ```

4. Apply database migrations:
   ```
   prisma migrate deploy
   ```

5. Run the application:
   ```
   python main.py
   ```

6. Seed the database (optional):
   ```
   python seed_db.py
   ```
   or via API:
   ```
   curl -X POST http://localhost:8000/api/seed-database
   ```

## API Endpoints

### Destinations
- `GET /api/destinations/random` - Get a random destination with clues
- `GET /api/destinations/options?destination_id=1` - Get multiple choice options for a destination
- `POST /api/destinations/check-answer` - Verify user answers
- `GET /api/destinations/{destination_id}` - Get a specific destination

### Users
- `POST /api/users` - Create a new user
- `GET /api/users/{username}` - Get user details
- `PUT /api/users/{username}/score` - Update user's score

### Game Features
- Random destination selection with customizable number of clues
- Multiple choice options generation
- Score tracking system (best tries, correct/incorrect answers)
- Fun facts and trivia for each destination

## Database Schema

### Destination Model
- `id`: Int (Primary Key)
- `name`: String (Unique)
- `clues`: String[]
- `funFacts`: String[]
- `trivia`: String[]
- `createdAt`: DateTime

### User Model
- `id`: Int (Primary Key)
- `username`: String (Unique)
- `bestTry`: Int
- `correctAnswers`: Int
- `incorrectAnswers`: Int
- `createdAt`: DateTime

## Development

The application uses:
- Flask for the web framework
- Prisma for database ORM
- PostgreSQL for the database
- Flask-CORS for handling cross-origin requests

## Testing

Run the test suite:
```
python -m unittest tests/test_routes.py
``` 