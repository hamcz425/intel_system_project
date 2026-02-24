import sqlite3
import logging
from datetime import datetime, timedelta
from config import DB_PATH

logger = logging.getLogger(__name__)

RETENTION_DAYS = 90  # 保留最近 90 天的记录


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS intel (
        id TEXT PRIMARY KEY,
        time TEXT,
        source TEXT,
        category TEXT,
        industry TEXT,
        companies TEXT,
        resource_type TEXT,
        money TEXT,
        region TEXT,
        title TEXT,
        content TEXT,
        url TEXT,
        created_at TEXT DEFAULT (datetime('now', 'localtime'))
    )''')
    conn.commit()
    conn.close()


def is_duplicate(record_id: str) -> bool:
    """检查该记录 ID 是否已存在于数据库中。"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT 1 FROM intel WHERE id = ? LIMIT 1", (record_id,))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def insert_record(record: dict) -> bool:
    """将记录写入数据库。若已存在则忽略，返回是否实际插入。"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute(
            """INSERT OR IGNORE INTO intel
               (id, time, source, category, industry, companies,
                resource_type, money, region, title, content, url)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record.get("id", ""),
                record.get("time", ""),
                record.get("source", ""),
                record.get("category", ""),
                record.get("industry", ""),
                record.get("companies", ""),
                record.get("resource_type", ""),
                record.get("money", ""),
                record.get("region", ""),
                record.get("title", ""),
                record.get("content", ""),
                record.get("url", ""),
            ),
        )
        inserted = c.rowcount > 0
        conn.commit()
        return inserted
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def cleanup_old_records(retention_days: int = RETENTION_DAYS) -> int:
    """删除超过 retention_days 天的旧记录，返回实际删除的条数。"""
    cutoff = (datetime.now() - timedelta(days=retention_days)).strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    try:
        c.execute("DELETE FROM intel WHERE created_at < ?", (cutoff,))
        deleted = c.rowcount
        conn.commit()
        if deleted > 0:
            logger.info(f"已清理 {deleted} 条超过 {retention_days} 天的旧记录")
        return deleted
    except Exception as e:
        conn.rollback()
        logger.error(f"清理旧记录时出错: {e}")
        return 0
    finally:
        conn.close()