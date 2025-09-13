from bson.objectid import ObjectId
from datetime import datetime, timedelta

def replace_mongo_id(doc):
    if doc:
        doc["id"] = str(doc["_id"])
        del doc["_id"]
    return doc

def format_date(date_str):
    """Format date for display"""
    if not date_str:
        return "Unknown date"
    
    try:
        # Try to parse ISO format
        date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return date_obj.strftime("%B %d, %Y")
    except:
        return date_str