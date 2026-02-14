import os
from dotenv import load_dotenv

# 加载 .env
load_dotenv()

OLLAMA_MODEL = "qwen2:7b"
DB_PATH = "intel.db"
CHECK_INTERVAL = 600

# 统一读取
WEBHOOK = os.getenv("WECHAT_WEBHOOK")
