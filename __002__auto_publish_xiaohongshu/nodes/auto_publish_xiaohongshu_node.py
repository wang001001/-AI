from playwright.sync_api import sync_playwright
from playwright.sync_api import TimeoutError as PlaywrightTimeout

import os

from __002__auto_publish_xiaohongshu.agent_state import AgentState
from common.path_utils import get_file_path

os.makedirs(get_file_path("cookie"), exist_ok=True)
PUBLISH_API_URL_KEYWORD = "edith.xiaohongshu.com/web_api/sns/v2/note"

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
        self.page.goto(self.PUBLISH_URL, wait_until="domcontentloaded")

        if not os.path.exists(self.COOKIE_PATH):
            print("[!] 请在打开的浏览器中完成小红书登录，登录完成后会自动继续...")
            self.wait_until_publish_ready()
            self.context.storage_state(path=self.COOKIE_PATH)
            print("[√] 登录状态已保存")
        self.wait_seconds(1)

    def wait_until_publish_ready(self, timeout_ms: int = 300000):
        selectors = [
            ".upload-content input.upload-input",
            ".edit-container input.d-text",
            ".creator-tab",
        ]
        deadline = timeout_ms
        step_ms = 3000
        while deadline > 0:
            for selector in selectors:
                locator = self.page.locator(selector).first
                if locator.count() > 0 and locator.is_visible():
                    print(f"[√] 检测到发布页元素：{selector}")
                    return True
            self.page.wait_for_timeout(step_ms)
            deadline -= step_ms
        raise RuntimeError("等待登录完成超时，请确认已在浏览器中完成登录。")

    def close(self):
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
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
                try:
                    class_name = tab.get_attribute("class") or ""
                    if "active" in class_name:
                        print(f"[√] 当前已位于 tab：{text}")
                        return True
                    tab.scroll_into_view_if_needed()
                    tab.click(timeout=5000, force=True)
                    print(f"[√] 已切换到 tab：{text}")
                    self.wait_seconds(1)
                    return True
                except Exception as e:
                    print(f"[!] 切换 tab 失败：{e}")
                    return False
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
        self.wait_seconds(1)
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

    def parse_publish_response(self, response) -> tuple[bool, str]:
        if response.status >= 400:
            return False, f"发布接口返回 HTTP {response.status}"

        try:
            payload = response.json()
        except Exception:
            payload = None

        if isinstance(payload, dict):
            success_flag = payload.get("success")
            code = payload.get("code")
            message = payload.get("msg") or payload.get("message") or ""
            data = payload.get("data") or {}

            if success_flag is False:
                return False, f"发布失败：{message or '接口返回 success=false'}"
            if code not in (None, 0, "0"):
                return False, f"发布失败：code={code} {message}".strip()

            note_id = None
            if isinstance(data, dict):
                note_id = data.get("note_id") or data.get("noteId") or data.get("id")

            if note_id:
                return True, f"小红书发布成功，note_id={note_id}"
            if success_flag is True or code in (0, "0"):
                return True, f"小红书发布成功{f'（{message}）' if message else ''}"

        return True, f"小红书发布成功（接口 HTTP {response.status}）"

    def wait_until_assets_ready(self, timeout_ms: int = 25000) -> bool:
        """
        等待图片上传和页面状态稳定后再点击发布，避免“刚上传完就点击”导致发布接口未触发。
        """
        print("[√] 等待图片上传完成后再点击发布...")
        self.wait_seconds(3)

        uploading_markers = [
            "上传中",
            "处理中",
            "正在处理",
            "正在上传",
            "生成封面中",
            "封面处理中",
        ]
        publish_btn = self.page.locator("button.d-button.bg-red").filter(has_text="发布")

        remaining = timeout_ms
        stable_rounds = 0
        while remaining > 0:
            body_text = ""
            try:
                body_text = self.page.locator("body").inner_text(timeout=1000)
            except Exception:
                pass

            has_uploading_marker = any(marker in body_text for marker in uploading_markers)
            is_ready = False
            try:
                is_ready = (
                    publish_btn.count() > 0
                    and publish_btn.first.is_visible()
                    and publish_btn.first.is_enabled()
                )
            except Exception:
                is_ready = False

            if is_ready and not has_uploading_marker:
                stable_rounds += 1
                if stable_rounds >= 2:
                    print("[√] 图片与页面状态已稳定，准备点击发布")
                    return True
            else:
                stable_rounds = 0

            self.page.wait_for_timeout(1000)
            remaining -= 1000

        print("[!] 未检测到明确的上传完成信号，额外等待 3 秒后继续尝试发布")
        self.wait_seconds(3)
        return True

    def click_publish_button(self) -> tuple[bool, str]:
        """
        自动点击发布按钮。
        页面元素：class 含 d-button、bg-red 的 button，内部文案为「发布」。

        :return: 点击成功返回 True，否则 False
        """
        try:
            publish_btn = self.page.get_by_role("button", name="发布", exact=True)
            publish_btn.wait_for(state="visible", timeout=5000)
            with self.page.expect_response(
                lambda response: PUBLISH_API_URL_KEYWORD in response.url and response.request.method == "POST",
                timeout=15000,
            ) as response_info:
                publish_btn.click(force=True)
            response = response_info.value
            print("[√] 已点击发布按钮")
            return self.parse_publish_response(response)
        except PlaywrightTimeout:
            print("[!] 点击发布后未检测到发布接口请求")
            return False, "未检测到真正的发布请求，请确认页面是否已准备完成"
        except Exception as e:
            print(f"[!] 点击发布按钮失败：{e}")
            return False, f"点击发布按钮失败：{e}"

    def wait_for_publish_result(self, timeout_ms: int = 30000):
        success_markers = [
            "发布成功",
            "审核中",
            "发布中",
            "去查看",
        ]
        failure_markers = [
            "发布失败",
            "网络异常",
            "上传失败",
            "请先完善",
            "请先选择",
            "标题不能为空",
        ]
        remaining = timeout_ms
        while remaining > 0:
            body_text = ""
            try:
                body_text = self.page.locator("body").inner_text(timeout=1000)
            except Exception:
                pass

            for marker in failure_markers:
                if marker in body_text:
                    return False, f"发布失败：{marker}"

            for marker in success_markers:
                if marker in body_text:
                    return True, f"小红书发布成功（{marker}）"

            current_url = self.page.url or ""
            if current_url and "/publish/publish" not in current_url:
                return True, f"小红书发布成功（页面已跳转到 {current_url}）"

            self.page.wait_for_timeout(1000)
            remaining -= 1000

        return False, "已点击发布，但未检测到明确成功信号，请人工确认页面结果"


def auto_publish_xiaohongshu(image_path_list, title, content):
    print("🚀 开始上传小红书...")
    xhs = XiaohongshuUploader(image_path_list, title, content)
    try:
        xhs.launch()
        # 页面通常默认落在图文页；若未切换成功，继续尝试当前页面上传。
        xhs.switch_to_tab("上传图文")
        if not xhs.upload_images():
            return False, "上传图片失败"
        if not xhs.fill_title_and_content():
            return False, "填充标题或正文失败"
        xhs.wait_until_assets_ready()
        success, message = xhs.click_publish_button()
        if not success:
            return False, message
        confirm_success, confirm_message = xhs.wait_for_publish_result()
        if confirm_success:
            return True, confirm_message
        return True, message
    finally:
        xhs.close()

def auto_publish_xiaohongshu_node(state: AgentState):
    """自动发布小红书"""
    image_path_list = state['xiaohongshu_tcm_post_image_path_list']
    title = state['xiaohongshu_tcm_post_title']
    content = state['xiaohongshu_tcm_post_content']
    success, message = auto_publish_xiaohongshu(image_path_list, title, content)
    state['output'] = message
    state['publish_success'] = success
    if not success:
        state['is_can_publish_xiaohongshu'] = False
    return state


if __name__ == '__main__':
    auto_publish_xiaohongshu_node(
        {"xiaohongshu_tcm_post_image_path_list": [get_file_path("picture/20260312160755沧州是个好.png")],
         "xiaohongshu_tcm_post_title": "沧州是个好地方",
         "xiaohongshu_tcm_post_content": "沧州好，是真的好，特别的好！"})
