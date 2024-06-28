import unittest
from app import create_app
from flask_pymongo import PyMongo
from bson import ObjectId
import json

class LeaderboardApiTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()
        cls.mongo = PyMongo(cls.app)

    def setUp(self):
        # Clear the database
        self.mongo.db.users.delete_many({})
        # Insert specific test data
        self.mongo.db.users.insert_many([
            {"_id": ObjectId(), "name": "John", "points": 50, "age": 25, "address": "123 Street", "photo_url": ""},
            {"_id": ObjectId(), "name": "Jane", "points": 50, "age": 25, "address": "456 Avenue", "photo_url": ""},
            {"_id": ObjectId(), "name": "Alice", "points": 30, "age": 20, "address": "789 Boulevard", "photo_url": ""}
        ])

    def test_create_user(self):
        data = {
            'name': 'Test User',
            'age': '30',
            'address': 'Test Address'
        }
        response = self.client.post('/users', data=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('user_id', response.json)

    def test_get_user(self):
        user = self.mongo.db.users.find_one({"name": "John"})
        user_id = str(user['_id'])
        response = self.client.get(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['name'], "John")

    def test_delete_user(self):
        user = self.mongo.db.users.find_one({"name": "Jane"})
        user_id = str(user['_id'])
        response = self.client.delete(f'/users/{user_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['message'], "User deleted")

    def test_update_user_points(self):
        user = self.mongo.db.users.find_one({"name": "Alice"})
        user_id = str(user['_id'])
        response = self.client.patch(f'/users/{user_id}/points', json={'increment': 10})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json['points'], 40)

    def test_get_leaderboard(self):
        # Insert test users
        self.mongo.db.users.insert_many([
            {'name': 'User1', 'photo_url': '', 'points': 50},
            {'name': 'User2', 'photo_url': '', 'points': 100}
        ])

        response = self.client.get('/leaderboard')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json), 5)
        self.assertEqual(response.json[0]['points'], 100)

    def test_get_grouped_users(self):
        # Insert test users
        self.mongo.db.users.insert_many([
            {'name': 'User1', 'photo_url': '', 'points': 50, 'age': 20},
            {'name': 'User2', 'photo_url': '', 'points': 50, 'age': 30},
            {'name': 'User3', 'photo_url': '', 'points': 100, 'age': 25}
        ])

        response = self.client.get('/grouped_by_points')
        self.assertEqual(response.status_code, 200)
        self.assertIn('50', response.json)
        self.assertIn('100', response.json)
        self.assertEqual(response.json['50']['average_age'], 25)
        self.assertEqual(response.json['100']['average_age'], 25)


if __name__ == '__main__':
    unittest.main()
