import requests
from config import WEBHOOK


def notify(record):
    print("\n📢 新情报提醒")
    print("标题:", record["title"])
    print("行业:", record["industry"])
    print("金额:", record["money"])
    print("地区:", record["region"])
    print("来源:", record["source"])

    print("当前WEBHOOK:", WEBHOOK)

    if not WEBHOOK:
        print("❌ 没有读取到企业微信Webhook")
        return

    content = f"""
### 📢 新情报提醒

> **标题：** {record['title']}
> **行业：** {record['industry']}
> **金额：** {record['money']}
> **地区：** {record['region']}
> **来源：** {record['source']}
"""

    data = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }

    try:
        r = requests.post(WEBHOOK, json=data, timeout=5)
        print("企业微信返回:", r.text)
    except Exception as e:
        print("推送异常:", e)
