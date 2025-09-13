from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
mongo_client = MongoClient(os.getenv("MONGO_URI"))

# Access database
news_reader_db = mongo_client["news_reader_db"]

# Collections
saved_articles_collection = news_reader_db["saved_articles"]