import json
import time
import random
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def extract_cookies(url: str, output_file: str = "cookies.json", headless: bool = False):
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=headless,
            args=[
                "--disable-blink-features=AutomationControlled",  # 绕过自动化检测
                "--no-sandbox"
            ]
        )

        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            # user_data_dir="./xhs_profile"  # 首次运行后取消注释，复用登录态
        )

        # 绕过 navigator.webdriver 检测
        context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined})
        """)

        page = context.new_page()

        try:
            # === 导航 + 智能等待 ===
            url_clean = url.strip()
            page.goto(url_clean, wait_until="domcontentloaded", timeout=60000)

            # 等待关键元素（避免页面未渲染完成）
            page.wait_for_selector("#searchKeyword, .feeds-container", timeout=10000)

            # 随机等待模拟真人（防反爬）
            page.wait_for_timeout(random.randint(2000, 5000))

            # === 提取 Cookies ===
            cookies = context.cookies()
            formatted_cookies = [{
                "name": c["name"],
                "value": c["value"],
                "domain": c.get("domain", ".xiaohongshu.com"),
                "path": c.get("path", "/"),
                "expires": c.get("expires", time.time() + 7 * 24 * 3600),
                "httpOnly": c.get("httpOnly", False),
                "secure": c.get("secure", True),
                "sameSite": c.get("sameSite", "Lax")
            } for c in cookies]

            # === 提取 localStorage ===
            localStorage = page.evaluate("""() => {
                return Array.from(Object.entries(localStorage)).map(([name, value]) => ({name, value}));
            }""")

            # === 输出结果 ===
            result = {
                "cookies": formatted_cookies,
                "origins": [{"origin": url_clean, "localStorage": localStorage}]
            }

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)

            print(f"✅ 提取成功: {len(cookies)} cookies + {len(localStorage)} localStorage 项")
            return result

        except PlaywrightTimeout as e:
            print(f"❌ 超时错误: {e}")
            # 截图调试
            page.screenshot(path="debug_timeout.png")
            raise
        finally:
            browser.close()


# 使用
extract_cookies("https://www.xiaohongshu.com/explore", headless=False)  # 首次建议 headless=False 手动登录