from playwright.sync_api import sync_playwright
import os
from agent_state import AgentState
from utils.path_utils import get_file_path

class XiaohongshuUploader:
    COOKIE_PATH = get_file_path("cookie/xiaohongshu_state.json")
    PUBLISH_URL = "https://creator.xiaohongshu.com/publish/publish?from=homepage&target=image&source=official"

    def __init__(self, image_path_list, title="", content=""):
        self.image_path_list = image_path_list
        self.title = title
        self.content = content
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None

    def launch(self):
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=False)

        if os.path.exists(self.COOKIE_PATH):
            print("[V] 加载已保存的登录状态...")
            self.context = self.browser.new_context(
                storage_state=self.COOKIE_PATH,
                permissions=["geolocation"],
                geolocation={"latitude": 31.2304, "longitude": 121.4737}
            )
        else:
            print("[!] 未检测到登录状态，创建新上下文...")
            self.context = self.browser.new_context(
                permissions=["geolocation"],
                geolocation={"latitude": 31.2304, "longitude": 121.4737}
            )

        self.page = self.context.new_page()
        self.page.goto(self.PUBLISH_URL)

        if not os.path.exists(self.COOKIE_PATH):
            input("请手动登录后按回车继续...")
            self.context.storage_state(path=self.COOKIE_PATH)
            print("[V] 登录状态已保存")
        self.wait_seconds(1)

    def switch_to_image_post(self):
        """切换到【上传图文】Tab，排除隐藏元素，并在必要时重试多种选择器。"""
        print("🔄 尝试切换到【上传图文】...")

        # 1) 首选: 使用 XPath，过滤掉隐藏在屏幕外的 Tab
        try:
            tab = self.page.locator(
                '//div[contains(@class,"creator-tab")][.//span[contains(@class,"title") and normalize-space(text())="上传图文"]]'
                '[not(contains(@style,"left: -9999px"))]'
            ).first
            tab.wait_for(state="visible", timeout=5000)
            tab.click()
            print("[V] 已切换到【上传图文】 (XPath 命中) ")
        except Exception as e1:
            print(f"[!] XPath 方式未命中，原因: {e1}")

            # 2) 退路: 用 has 定位可见的 creator-tab
            try:
                tab2 = self.page.locator('div.creator-tab').filter(
                    has=self.page.locator('span.title', has_text="上传图文")
                ).first
                tab2.wait_for(state="visible", timeout=5000)
                tab2.click()
                print("[V] 已切换到【上传图文】 (has 过滤命中) ")
            except Exception as e2:
                print(f"[!] has 过滤方式未命中，原因: {e2}")

                # 3) 最后退路: 直接点文本 (Playwright 会优先点可见元素)
                try:
                    self.page.get_by_text("上传图文", exact=True).first.click()
                    print("[V] 已切换到【上传图文】 (文本匹配命中) ")
                except Exception as e3:
                    print(f"[X] 切换到【上传图文】失败: {e3}")

        # 等待图文上传区域的图片文件选择器出现 (避免还停留在"上传视频")
        try:
            # 图文面板一般会出现一个接收图片的 input[type=file]; 为稳妥，这里只校验出现任意文件 input
            self.page.wait_for_selector('input[type="file"]', timeout=8000)
            print("[V] 图文上传区域已就绪")
        except:
            print("[!] 未检测到图文上传的文件输入框，稍后上传可能失败")

    def upload_images(self):
        print("🖼️ 正在上传图片...")
        self.page.wait_for_selector('input[type="file"]', timeout=10000)
        file_inputs = self.page.query_selector_all('input[type="file"]')
        if file_inputs:
            file_inputs[0].set_input_files(self.image_path_list)
            print(f"[V] 已上传 {len(self.image_path_list)} 张图片")
        else:
            print("[x] 未找到文件上传输入框")

    def fill_title_and_content(self):
        print("📝 正在填写标题和正文...")
        # 填写标题
        try:
            title_input = self.page.wait_for_selector('input.d-text[placeholder*="填写标题"]', timeout=10000)
            title_input.fill(self.title)
            print(f"[V] 标题已填写: {self.title}")
        except:
            print("[x] 未找到标题输入框")

        # 填写正文
        try:
            editor = self.page.wait_for_selector('.tiptap[contenteditable="true"]', timeout=10000)
            editor.click()
            editor.type(self.content)
            print(f"[V] 正文已填写: {self.content}")
        except:
            print("[x] 未找到正文编辑器")

    def submit_post(self):
        self.wait_seconds(3)
        print("🚀 正在尝试点击发布按钮...")
        try:
            # 等待"发布"按钮出现并可点击
            self.page.wait_for_selector('button:has-text("发布")', timeout=10000)
            publish_button = self.page.query_selector('button:has-text("发布")')

            if publish_button:
                publish_button.click()
                print("[V] 发布按钮已点击")
            else:
                print("[!] 未找到发布按钮")
        except Exception as e:
            print(f"[X] 发布失败: {e}")

    def close(self):
        # 等待4秒
        self.wait_seconds(6)
        self.browser.close()
        self.playwright.stop()

    def wait_seconds(self, seconds):
        print(f"⏳ 等待 {seconds} 秒...")
        self.page.wait_for_timeout(seconds * 1000)

def auto_publish_xiaohongshu(image_path_list, title, content):
    print("📝 开始上传小红书...")
    xhs = XiaohongshuUploader(image_path_list, title, content)
    xhs.launch()
    xhs.switch_to_image_post()
    xhs.upload_images()
    xhs.fill_title_and_content()
    # 最后点击发布
    xhs.submit_post()
    xhs.close()

def publish_node(state: AgentState):
    """小红书发布节点：只有通过校验后才执行发布"""
    if state.get("is_can_publish_xiaohongshu"):
        print("[V] 校验通过，开始自动发布小红书...")
        auto_publish_xiaohongshu(
            image_path_list=state["xiaohongshu_tcm_post_image_path_list"],
            title=state["xiaohongshu_tcm_post_title"],
            content=state["xiaohongshu_tcm_post_content"]
        )
        state["output"] = "小红书发布成功！"
    else:
        print(f"[X] 发布被阻止：{state.get('output', '未知原因')}")
    return state
