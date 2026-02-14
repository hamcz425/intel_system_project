
import requests, json
from datetime import datetime

def fetch_sse_announcements():
    url = "http://query.sse.com.cn/security/stock/queryCompanyBulletin.do"
    headers = {"Referer": "http://www.sse.com.cn/", "User-Agent": "Mozilla/5.0"}
    today = datetime.now().strftime("%Y-%m-%d")

    params = {
        "isPagination": "true",
        "pageHelp.pageSize": 5,
        "pageHelp.pageNo": 1,
        "beginDate": today,
        "endDate": today
    }

    r = requests.get(url, headers=headers, params=params, timeout=10)
    data = json.loads(r.text[r.text.find("{"):r.text.rfind("}")+1])
    results = []

    for item in data.get("result", []):
        results.append({
            "time": item.get("SSEDATE", today),
            "source": "SSE",
            "category": "公告",
            "title": item.get("TITLE", ""),
            "content": item.get("TITLE", ""),
            "url": item.get("URL", "")
        })
    return results
