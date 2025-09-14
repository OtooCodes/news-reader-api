from fastapi import FastAPI, Form, HTTPException, status
from pydantic import BaseModel
from bson.objectid import ObjectId
from typing import Annotated
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

from db import saved_articles_collection
from utils import replace_mongo_id, format_date

# Load environment variables
load_dotenv()

# NewsAPI configuration
NEWS_API_KEY = os.getenv("NEWS_API_KEY")
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"

# API tags metadata
tags_metadata = [
    {"name": "News", "description": "Fetch live news articles from NewsAPI"},
    {"name": "Saved Articles", "description": "Manage your saved articles"},
    {"name": "Digest", "description": "Get your daily news digest"},
]

# Initialize FastAPI app
app = FastAPI(
    title="News Reader API",
    description="API for fetching news articles and saving them to your personal collection",
    openapi_tags=tags_metadata,
)


# -------------------------------
# Homepage endpoint
# -------------------------------
@app.get("/", tags=["News"])
def get_home():
    """Welcome message for the API"""
    return {"message": "Welcome to News Reader API!"}


# -------------------------------
# News endpoints
# -------------------------------
@app.get("/news/{category}", tags=["News"])
def get_news_by_category(category: str, country: str = "us", page_size: int = 10):
    """
    Fetch news articles from NewsAPI based on category.

    - **category**: News category (business, entertainment, general, health, science, sports, technology)
    - **country**: Country code (default: us)
    - **page_size**: Number of articles to return (default: 10, max: 100)
    """
    if not NEWS_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="NewsAPI configuration missing",
        )

    valid_categories = [
        "business", "entertainment", "general",
        "health", "science", "sports", "technology"
    ]

    if category.lower() not in valid_categories:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid category. Must be one of: {', '.join(valid_categories)}",
        )

    params = {
        "category": category.lower(),
        "country": country.lower(),
        "pageSize": min(page_size, 100),
        "apiKey": NEWS_API_KEY,
    }

    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()

        if data["status"] != "ok":
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="NewsAPI returned an error",
            )

        # Format articles
        articles = [
            {
                "title": article.get("title", "No title"),
                "description": article.get("description", "No description"),
                "url": article.get("url", ""),
                "urlToImage": article.get("urlToImage", ""),
                "publishedAt": format_date(article.get("publishedAt")),
                "source": article.get("source", {}).get("name", "Unknown source"),
            }
            for article in data.get("articles", [])
        ]

        return {
            "category": category,
            "totalResults": data.get("totalResults", 0),
            "articles": articles,
        }

    except requests.exceptions.RequestException as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error fetching news: {str(e)}",
        )


# -------------------------------
# Saved articles endpoints
# -------------------------------
@app.post("/saved", tags=["Saved Articles"])
def save_article(
    title: Annotated[str, Form()],
    url: Annotated[str, Form()],
    category: Annotated[str, Form()],
    description: Annotated[str, Form()] = "",
):
    """Save an article to the database"""

    # Check if article already exists
    if saved_articles_collection.find_one({"url": url}):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Article already saved",
        )

    # Insert article
    article_data = {
        "title": title,
        "url": url,
        "category": category,
        "description": description,
        "date_saved": datetime.utcnow().isoformat(),
    }

    result = saved_articles_collection.insert_one(article_data)

    return {"message": "Article saved successfully!", "id": str(result.inserted_id)}


@app.get("/saved", tags=["Saved Articles"])
def get_saved_articles():
    """Retrieve all articles saved by the user"""
    saved_articles = saved_articles_collection.find().sort("date_saved", -1).to_list()
    return {
        "count": len(saved_articles),
        "articles": list(map(replace_mongo_id, saved_articles)),
    }


@app.delete("/saved/{article_id}", tags=["Saved Articles"])
def delete_saved_article(article_id: str):
    """Delete a saved article by ID"""
    if not ObjectId.is_valid(article_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid article ID",
        )

    delete_result = saved_articles_collection.delete_one({"_id": ObjectId(article_id)})

    if not delete_result.deleted_count:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    return {"message": "Article deleted successfully!"}


# -------------------------------
# Digest endpoints
# -------------------------------
@app.get("/digest", tags=["Digest"])
def get_daily_digest():
    """Get the last five saved articles from the last 24 hours as a daily digest"""
    yesterday = datetime.utcnow() - timedelta(days=1)

    recent_articles = (
        saved_articles_collection.find({"date_saved": {"$gte": yesterday.isoformat()}})
        .sort("date_saved", -1)
        .limit(5)
        .to_list()
    )

    return {
        "date": datetime.utcnow().date().isoformat(),
        "count": len(recent_articles),
        "articles": list(map(replace_mongo_id, recent_articles)),
    }
