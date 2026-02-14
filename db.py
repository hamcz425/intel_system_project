
import sqlite3
from config import DB_PATH

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
        url TEXT
    )''')
    conn.commit()
    conn.close()
