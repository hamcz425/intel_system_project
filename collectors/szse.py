
import requests
from datetime import datetime

def fetch_szse_announcements():
    url = "http://www.szse.cn/api/disc/announcement/annList"
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "http://www.szse.cn/"}
    payload = {
        "seDate": [datetime.now().strftime("%Y-%m-%d"), datetime.now().strftime("%Y-%m-%d")],
        "channelCode": ["listedNotice_disc"],
        "pageSize": 5,
        "pageNum": 1
    }

    r = requests.post(url, headers=headers, json=payload, timeout=10)
    data = r.json()
    results = []

    for item in data.get("data", []):
        results.append({
            "time": item.get("publishTime"),
            "source": "SZSE",
            "category": "公告",
            "title": item.get("title"),
            "content": item.get("title"),
            "url": "http://www.szse.cn" + item.get("pdfPath", "")
        })
    return results
