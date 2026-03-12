from playwright.sync_api import sync_playwright

import os

from __002__auto_publish_xiaohongshu.agent_state import AgentState
from common.path_utils import get_file_path

os.makedirs(get_file_path("cookie"), exist_ok=True)

class XiaohongshuUploader:
    COOKIE_PATH = get_file_path("cookie/xiaohongshu_state.json")
    PUBLISH_URL = "https://creator.xiaohongshu.com/publish/publish?from=homepage&target=image&source=official"

    def __init__(self, image_path_list, title="", content=""):
        self.image_path_list = image_path_list
        self.title = title
        self.content = content
        # playwright,作用就是操作页面
        self.playwright = None
        # 浏览器
        self.browser = None
        # 上下文: 浏览器的会话, 可以保存登录状态等等记忆
        self.context = None
        # 页面
        self.page = None

    def launch(self):
        # 启动playwright
        self.playwright = sync_playwright().start()
        # 启动浏览器
        self.browser = self.playwright.chromium.launch(headless=False)

        if os.path.exists(self.COOKIE_PATH):
            print("[√] 加载已保存的登录状态...")
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
            print("[√] 登录状态已保存")
        self.wait_seconds(1)

    def close(self):
        # 等待6秒
        self.wait_seconds(6)
        self.browser.close()
        self.playwright.stop()

    def wait_seconds(self, seconds):
        print(f"⏳ 等待 {seconds} 秒...")
        self.page.wait_for_timeout(seconds * 1000)

    def switch_to_tab(self, text: str) -> bool:
        """
        根据 tab 文案切换到对应 tab 页。
        文案需与页面上 .creator-tab .title 的文本一致，如：上传视频、上传图文、写长文。

        :param text: tab 标题文案，如 "上传图文"
        :return: 找到并点击成功返回 True，否则 False
        """
        locator = self.page.locator(".creator-tab").filter(has_text=text)
        for tab in locator.all():
            if tab.is_visible():
                tab.click()
                print(f"[√] 已切换到 tab：{text}")
                self.wait_seconds(1)
                return True
        print(f"[!] 未找到可见的 tab：{text}")
        return False

    def upload_images(self) -> bool:
        """
        在「上传图文」区域通过隐藏的 input[type=file] 自动上传图片。
        页面元素：.upload-content 内的 input.upload-input（accept=".jpg,.jpeg,.png,.webp"）。

        :param image_path_list: 本地图片路径列表；不传则使用 self.image_path_list
        :return: 全部上传成功返回 True，否则 False
        """
        file_input = self.page.locator(".upload-content input.upload-input")
        try:
            file_input.set_input_files(self.image_path_list)
        except Exception as e:
            print(f"[!] 上传图片失败：{e}")
            return False

        print(f"[√] 已选择 {len(self.image_path_list)} 张图片")
        self.wait_seconds(2)
        return True

    def fill_title_and_content(
        self,
        title: str | None = None,
        content: str | None = None,
    ) -> bool:
        """
        自动填充标题和正文。
        标题：.edit-container 内 input.d-text（placeholder="填写标题会有更多赞哦"）
        正文：.tiptap.ProseMirror  contenteditable 富文本区域。

        :param title: 标题文案；不传则使用 self.title
        :param content: 正文文案；不传则使用 self.content
        :return: 成功返回 True，否则 False
        """
        title_text = title if title is not None else self.title
        content_text = content if content is not None else self.content

        try:
            title_input = self.page.locator(".edit-container input.d-text")
            title_input.wait_for(state="visible", timeout=5000)
            title_input.fill(title_text)
            print(f"[√] 已填充标题：{title_text[:20]}{'…' if len(title_text) > 20 else ''}")

            content_editor = self.page.locator("div.tiptap.ProseMirror")
            content_editor.wait_for(state="visible", timeout=5000)
            content_editor.click()
            content_editor.fill(content_text)
            print(f"[√] 已填充正文：{len(content_text)} 字")

            self.wait_seconds(1)
            return True
        except Exception as e:
            print(f"[!] 填充标题/正文失败：{e}")
            return False

    def click_publish_button(self) -> bool:
        """
        自动点击发布按钮。
        页面元素：class 含 d-button、bg-red 的 button，内部文案为「发布」。

        :return: 点击成功返回 True，否则 False
        """
        try:
            publish_btn = self.page.locator("button.d-button.bg-red").filter(has_text="发布")
            publish_btn.wait_for(state="visible", timeout=5000)
            publish_btn.click()
            print("[√] 已点击发布按钮")
            self.wait_seconds(2)
            return True
        except Exception as e:
            print(f"[!] 点击发布按钮失败：{e}")
            return False


def auto_publish_xiaohongshu(image_path_list, title, content):
    print("🚀 开始上传小红书...")
    xhs = XiaohongshuUploader(image_path_list, title, content)
    xhs.launch()
    # xhs.switch_to_tab("上传视频")
    xhs.upload_images()
    xhs.fill_title_and_content()
    xhs.wait_seconds(10)
    xhs.click_publish_button()
    xhs.close()

def auto_publish_xiaohongshu_node(state: AgentState):
    """自动发布小红书"""
    image_path_list = state['xiaohongshu_tcm_post_image_path_list']
    title = state['xiaohongshu_tcm_post_title']
    content = state['xiaohongshu_tcm_post_content']
    auto_publish_xiaohongshu(image_path_list, title, content)
    state['output'] = '小红书发布成功'
    return state


if __name__ == '__main__':
    auto_publish_xiaohongshu_node(
        {"xiaohongshu_tcm_post_image_path_list": [get_file_path("picture/20260312160755沧州是个好.png")],
         "xiaohongshu_tcm_post_title": "沧州是个好地方",
         "xiaohongshu_tcm_post_content": "沧州好，是真的好，特别的好！"})