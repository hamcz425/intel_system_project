
import hashlib
from db import init_db
from ai_engine import structure_text

def process_item(item):
    record_id = hashlib.md5((item["title"] + item["source"]).encode()).hexdigest()
    ai_data = structure_text(item["content"])

    record = {
        "id": record_id,
        "time": item["time"],
        "source": item["source"],
        "category": item["category"],
        "industry": ai_data.get("industry", ""),
        "companies": ai_data.get("companies", ""),
        "resource_type": ai_data.get("resource_type", ""),
        "money": ai_data.get("money", ""),
        "region": ai_data.get("region", ""),
        "title": item["title"],
        "content": item["content"],
        "url": item["url"]
    }
    return record
