
import requests
from bs4 import BeautifulSoup
from datetime import datetime

def fetch_policy_news():
    url = "https://www.gov.cn/zhengce/zuixin.htm"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")
    data = []
    for a in soup.find_all("a"):
        title = a.get_text(strip=True)
        if len(title) > 15:
            data.append({
                "time": str(datetime.now()),
                "source": "gov.cn",
                "category": "政策",
                "title": title,
                "content": title,
                "url": a.get("href")
            })
    return data
