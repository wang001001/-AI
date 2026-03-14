import hashlib
import json
import threading
import time
from pathlib import Path

from common.path_utils import get_file_path


CACHE_DIR = Path(get_file_path("cookie"))
CACHE_FILE = CACHE_DIR / "workflow_cache.json"
CACHE_LOCK = threading.Lock()
CACHE_TTL_SECONDS = 60 * 60


def _normalize_text(user_input: str) -> str:
    return " ".join(user_input.strip().split())


def _cache_key(user_input: str) -> str:
    normalized = _normalize_text(user_input)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def _load_cache() -> dict:
    if not CACHE_FILE.exists():
        return {}
    try:
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write_cache(cache_data: dict):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2), encoding="utf-8")


def get_cached_generation(user_input: str) -> dict | None:
    key = _cache_key(user_input)
    with CACHE_LOCK:
        cache_data = _load_cache()
        payload = cache_data.get(key)

    if not payload:
        return None

    if time.time() - payload.get("created_at", 0) > CACHE_TTL_SECONDS:
        return None

    image_paths = payload.get("xiaohongshu_tcm_post_image_path_list", [])
    if not image_paths:
        return None

    if not all(Path(path).exists() for path in image_paths):
        return None

    return payload


def save_cached_generation(user_input: str, state: dict):
    if not state.get("xiaohongshu_tcm_post_title"):
        return
    if not state.get("xiaohongshu_tcm_post_content"):
        return
    if not state.get("xiaohongshu_tcm_post_image_path_list"):
        return

    key = _cache_key(user_input)
    payload = {
        "created_at": time.time(),
        "xiaohongshu_tcm_post_title": state.get("xiaohongshu_tcm_post_title", ""),
        "xiaohongshu_tcm_post_content": state.get("xiaohongshu_tcm_post_content", ""),
        "xiaohongshu_tcm_post_site": state.get("xiaohongshu_tcm_post_site", ""),
        "xiaohongshu_tcm_post_image_path_list": state.get("xiaohongshu_tcm_post_image_path_list", []),
    }

    with CACHE_LOCK:
        cache_data = _load_cache()
        cache_data[key] = payload
        _write_cache(cache_data)
