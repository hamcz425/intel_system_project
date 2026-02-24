from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import logging

logger = logging.getLogger(__name__)

URL = "https://www.gov.cn/zhengce/zuixin/home.htm"

MAX_RETRIES = 3


def _build_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )


def _extract_policies(driver):
    """等待页面加载完成后提取政策条目，同时尝试抓取发布时间。"""
    # 等待至少一条政策链接出现，最多等 15 秒
    try:
        WebDriverWait(driver, 15).until(
            lambda d: any(
                "/zhengce/" in (a.get_attribute("href") or "")
                or "/yaowen/" in (a.get_attribute("href") or "")
                for a in d.find_elements(By.TAG_NAME, "a")
                if a.text.strip()
            )
        )
    except Exception:
        logger.warning("等待政策链接超时，尝试使用已加载内容")

    seen = set()
    policies = []

    # 优先从 li 元素中同时提取标题、链接和时间
    for li in driver.find_elements(By.TAG_NAME, "li"):
        try:
            a_tags = li.find_elements(By.TAG_NAME, "a")
            if not a_tags:
                continue
            a = a_tags[0]
            href = a.get_attribute("href") or ""
            title = a.text.strip()

            if not title or not ("/zhengce/" in href or "/yaowen/" in href):
                continue
            if href in seen:
                continue
            seen.add(href)

            # 尝试从同一 li 中找日期文本（格式如 2026-02-24）
            li_text = li.text
            pub_time = ""
            for part in li_text.replace(title, "").split():
                if len(part) == 10 and part.count("-") == 2:
                    pub_time = part
                    break

            policies.append({
                "title": title,
                "url": href,
                "link": href,
                "source": "guowuyuan",
                "content": title,
                "time": pub_time,
                "category": "政策",
            })

            if len(policies) >= 10:
                break

        except Exception as e:
            logger.debug(f"解析 li 条目时出错: {e}")
            continue

    return policies


def fetch_gov_policies():
    """抓取国务院最新政策，失败时最多重试 MAX_RETRIES 次。"""
    for attempt in range(1, MAX_RETRIES + 1):
        driver = None
        try:
            logger.info(f"国务院政策抓取 第 {attempt} 次尝试")
            driver = _build_driver()
            driver.get(URL)
            policies = _extract_policies(driver)
            if policies:
                logger.info(f"成功抓取 {len(policies)} 条政策")
                return policies
            else:
                logger.warning(f"第 {attempt} 次未抓取到内容，准备重试")
        except Exception as e:
            logger.error(f"第 {attempt} 次抓取异常: {e}")
        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass
        if attempt < MAX_RETRIES:
            time.sleep(3)

    logger.error("国务院政策抓取全部失败，返回空列表")
    return []


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = fetch_gov_policies()
    print(f"抓到 {len(result)} 条政策")
    for r in result:
        print(r)