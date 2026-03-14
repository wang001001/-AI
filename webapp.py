import threading
from pathlib import Path
import re

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from __002__auto_publish_xiaohongshu.langgraph_auto_publish_xiaohongshu import run_workflow_with_options
from common.path_utils import get_file_path


ROOT_DIR = Path(get_file_path(""))
WEB_DIR = ROOT_DIR / "web"
PICTURE_DIR = ROOT_DIR / "picture"
COOKIE_FILE = ROOT_DIR / "cookie" / "xiaohongshu_state.json"

publish_lock = threading.Lock()

app = FastAPI(
    title="小红书自动发布",
    description="通过前端输入主题文本，自动生成文案、配图并发布到小红书。",
)

app.mount("/assets", StaticFiles(directory=str(WEB_DIR / "assets")), name="assets")
app.mount("/generated", StaticFiles(directory=str(PICTURE_DIR)), name="generated")


class PublishRequest(BaseModel):
    text: str = Field(..., min_length=1, description="用户输入的主题文本")
    image_count: int | None = Field(None, ge=1, le=5, description="要生成并发布的图片数量")


CHINESE_DIGIT_MAP = {
    "一": 1,
    "二": 2,
    "两": 2,
    "三": 3,
    "四": 4,
    "五": 5,
}


def infer_image_count_from_text(text: str) -> int | None:
    text = text or ""
    m = re.search(r"([1-5])\s*张(?:图|图片)?", text)
    if m:
        return int(m.group(1))

    m = re.search(r"([一二两三四五])\s*张(?:图|图片)?", text)
    if m:
        return CHINESE_DIGIT_MAP.get(m.group(1))
    return None


def image_path_to_url(image_path: str) -> str | None:
    if not image_path:
        return None

    file_path = Path(image_path)
    if not file_path.exists():
        return None

    try:
        relative_path = file_path.relative_to(PICTURE_DIR)
    except ValueError:
        return None
    return f"/generated/{relative_path.as_posix()}"


def serialize_result(result: dict) -> dict:
    image_paths = result.get("xiaohongshu_tcm_post_image_path_list", [])
    image_urls = [url for url in (image_path_to_url(path) for path in image_paths) if url]
    output = result.get("output", "")

    return {
        "input": result.get("input", ""),
        "title": result.get("xiaohongshu_tcm_post_title", ""),
        "content": result.get("xiaohongshu_tcm_post_content", ""),
        "site": result.get("xiaohongshu_tcm_post_site", ""),
        "image_count": len(image_paths),
        "image_paths": image_paths,
        "image_urls": image_urls,
        "is_can_publish_xiaohongshu": result.get("is_can_publish_xiaohongshu", False),
        "output": output,
        "published": result.get("publish_success", False),
        "used_cache": result.get("used_cache", False),
    }


@app.get("/")
def index():
    return FileResponse(WEB_DIR / "index.html")


@app.get("/api/health")
def health():
    return {
        "ok": True,
        "has_login_state": COOKIE_FILE.exists(),
        "is_busy": publish_lock.locked(),
    }


@app.post("/api/publish")
def publish(payload: PublishRequest):
    user_text = payload.text.strip()
    if not user_text:
        raise HTTPException(status_code=400, detail="请输入主题文本。")
    inferred_count = infer_image_count_from_text(user_text)
    requested_count = payload.image_count if payload.image_count is not None else inferred_count
    image_count = max(1, min(requested_count if requested_count is not None else 1, 5))

    if not publish_lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="当前已有一个发布任务在运行，请稍后重试。")

    try:
        result = run_workflow_with_options(user_text, image_count=image_count)
        return serialize_result(result)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"发布流程执行失败: {exc}") from exc
    finally:
        publish_lock.release()
