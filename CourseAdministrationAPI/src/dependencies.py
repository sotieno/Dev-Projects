# dependencies.py

from pymongo import MongoClient

# Connect to MongoDB using the PyMongo
client = MongoClient('mongodb://localhost:27017/')

# Access the 'courses' database in MongoDB
db = client['courses']

# Dependency to inject the 'db' instance into routes
def get_db():
    return db
