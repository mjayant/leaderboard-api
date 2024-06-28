import os
from faker import Faker
from pymongo import MongoClient
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize Faker
fake = Faker()

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.get_database()

def create_fake_user():
    return {
        "name": fake.name(),
        "age": fake.random_int(min=18, max=80),
        "address": fake.address(),
        "points": fake.random_int(min=0, max=100),
        "photo_url": fake.image_url()
    }

def populate_db(n=10):
    users = [create_fake_user() for _ in range(n)]
    result = db.users.insert_many(users)
    return result.inserted_ids

if __name__ == "__main__":
    num_users = int(input("Enter the number of users to create: "))
    user_ids = populate_db(num_users)
    print(f"Inserted {len(user_ids)} users into the database.")
