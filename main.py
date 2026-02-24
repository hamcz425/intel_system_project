import time
import logging
from datetime import datetime

from db import init_db, is_duplicate, insert_record, cleanup_old_records
from collectors.policy import fetch_policy_news
from collectors.sse import fetch_sse_announcements
from collectors.szse import fetch_szse_announcements
from sources.gov_council import fetch_gov_policies
from processor import process_item
from notifier import notify
from config import CHECK_INTERVAL

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s - %(message)s",
    handlers=[
        logging.FileHandler("system.log", encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

SOURCES = [
    ("政策新闻", fetch_policy_news),
    ("上交所", fetch_sse_announcements),
    ("深交所", fetch_szse_announcements),
    ("国务院", fetch_gov_policies),
]


def fetch_all_items():
    """逐个数据源抓取，单个来源失败不影响其他来源。"""
    items = []
    for name, fetcher in SOURCES:
        try:
            results = fetcher()
            logger.info(f"[{name}] 抓取到 {len(results)} 条")
            items.extend(results)
        except Exception as e:
            logger.error(f"[{name}] 抓取失败: {e}")
    return items


def run():
    init_db()
    logger.info("🚀 综合资讯系统启动")

    last_cleanup_day = None  # 记录上次清理的日期

    while True:
        try:
            # 每天只执行一次清理（当天第一轮时触发）
            today = datetime.now().date()
            if last_cleanup_day != today:
                cleanup_old_records()
                last_cleanup_day = today

            items = fetch_all_items()
            pushed = 0

            for item in items:
                try:
                    record = process_item(item)
                    if not record:
                        continue

                    # 去重：已存在则跳过
                    if is_duplicate(record["id"]):
                        logger.debug(f"跳过重复记录: {record['title']}")
                        continue

                    # 推送通知
                    notify(record)

                    # 写库，确认推送后才持久化
                    insert_record(record)
                    pushed += 1

                except Exception as e:
                    logger.error(f"处理条目失败: {item.get('title', '')} - {e}")

            logger.info(
                f"本轮完成，共推送 {pushed} 条新内容，"
                f"等待 {CHECK_INTERVAL} 秒后进入下一轮..."
            )

        except Exception as e:
            logger.error(f"主循环异常: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    run()