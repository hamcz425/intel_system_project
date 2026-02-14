import time
from datetime import datetime

from db import init_db
from collectors.policy import fetch_policy_news
from collectors.sse import fetch_sse_announcements
from collectors.szse import fetch_szse_announcements
from processor import process_item
from notifier import notify
from config import CHECK_INTERVAL


def run():
    init_db()
    print("🚀 综合资讯系统启动")

    while True:
        try:
            items = []

            items += fetch_policy_news()
            items += fetch_sse_announcements()
            items += fetch_szse_announcements()

            for item in items:
                record = process_item(item)
                if record:
                    notify(record)

            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏳ 等待下一轮...")

        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 发生错误: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()
