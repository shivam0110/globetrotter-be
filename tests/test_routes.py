import unittest
import json
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.models import prisma

class TestRoutes(unittest.TestCase):
    def setUp(self):
        """Set up test client and app context"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # Create a test destination if needed
        self.test_destination = prisma.destination.upsert(
            where={"name": "Test City, Test Country"},
            data={
                "create": {
                    "name": "Test City, Test Country",
                    "clues": ["Test clue 1", "Test clue 2"],
                    "funFacts": ["Test fun fact"],
                    "trivia": ["Test trivia"]
                },
                "update": {}
            }
        )
        
        # Create a test user if needed
        self.test_user = prisma.user.upsert(
            where={"username": "testuser"},
            data={
                "create": {
                    "username": "testuser",
                    "bestTry": 3,
                    "correctAnswers": 5,
                    "incorrectAnswers": 2
                },
                "update": {}
            }
        )

    def tearDown(self):
        """Clean up after tests"""
        # Delete test data if needed
        pass

    def test_random_destination(self):
        """Test getting a random destination"""
        response = self.client.get('/api/destinations/random')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('success' in data)
        self.assertTrue(data['success'])
        self.assertTrue('name' in data)
        self.assertTrue('clues' in data)

    def test_create_user(self):
        """Test creating a new user"""
        response = self.client.post(
            '/api/users',
            data=json.dumps({'username': 'newuser'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertTrue('success' in data)
        self.assertTrue(data['success'])
        self.assertEqual(data['username'], 'newuser')
        
        # Clean up - delete the created user
        prisma.user.delete(where={"username": "newuser"})

    def test_get_user(self):
        """Test getting user details"""
        response = self.client.get(f'/api/users/{self.test_user.username}')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('success' in data)
        self.assertTrue(data['success'])
        self.assertEqual(data['username'], self.test_user.username)
        self.assertEqual(data['best_try'], self.test_user.bestTry)

    def test_update_user_score(self):
        """Test updating a user's score"""
        new_score = 2  # Better than current score of 3
        response = self.client.put(
            f'/api/users/{self.test_user.username}/score',
            data=json.dumps({'score': new_score}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('success' in data)
        self.assertTrue(data['success'])
        self.assertEqual(data['best_try'], new_score)
        
        # Reset the score for future tests
        prisma.user.update(
            where={"username": self.test_user.username},
            data={"bestTry": 3}
        )

    def test_nonexistent_user(self):
        """Test getting a user that doesn't exist"""
        response = self.client.get('/api/users/nonexistentuser')
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertFalse(data['success'])
        self.assertTrue('message' in data)

    def test_seed_database(self):
        """Test the seed database endpoint"""
        response = self.client.post('/api/seed-database')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue('message' in data)

if __name__ == '__main__':
    unittest.main() 