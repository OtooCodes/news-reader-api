

**News Reader API**

A FastAPI-based news reader application that fetches articles from us NewsAPI and allows users to save their favorite articles to a MongoDB database.

Features
Fetch live news articles by category from NewsAPI

Save articles to a personal collection

View all saved articles

Get a daily digest of the last 5 saved articles

Delete saved articles

Prerequisites

Python 3.7+

MongoDB (local or Atlas)

NewsAPI account (free tier available)

[**VIEW API**](https://news-reader-api.vercel.app/docs)


Installation

Clone the repository:

git clone <your-repo-url>

cd news-reader-api

News Endpoints
1. Get News by Category

Endpoint: GET /news/{category}

Response:

json
{
  "category": "technology",
  "totalResults": 70,
  "articles": [
    {
    
      "title": "Apple Announces New iPhone", 
      "description": "Apple unveiled its latest iPhone with groundbreaking features...",
      "url": "https://example.com/apple-iphone",
      "urlToImage": "https://example.com/image.jpg",
      "publishedAt": "October 15, 2023",
      "source": "Tech News"
    },
    {
      "title": "Google's New AI Breakthrough",
      "description": "Google researchers have developed a new AI model that...",
      "url": "https://example.com/google-ai",
      "urlToImage": "https://example.com/ai-image.jpg",
      "publishedAt": "October 14, 2023",
      "source": "AI Daily"
    }
  ]
}





