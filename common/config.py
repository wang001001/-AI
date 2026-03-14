import os
from dotenv import load_dotenv

from common.path_utils import get_file_path

# 优先读取仓库根目录下的本地 .env，避免依赖作者机器上的固定路径。
load_dotenv(get_file_path(".env"))

def _int(key: str, default: int = 0) -> int:
    val = os.getenv(key)
    return int(val) if val is not None else default


def _str(key: str, default: str = "") -> str:
    return os.getenv(key) or default


def _bool(key: str, default: bool = False) -> bool:
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in {"1", "true", "yes", "on"}


class Config:
    def __init__(self):
        # 文本模型：默认使用 DeepSeek 的 OpenAI 兼容接口
        self.DEEPSEEK_API_KEY = _str("DEEPSEEK_API_KEY")
        self.DEEPSEEK_BASE_URL = _str("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
        self.DEEPSEEK_MODEL = _str("DEEPSEEK_MODEL", "deepseek-chat")

        # 图片模型：默认使用 Qwen 图像生成
        self.QWEN_API_KEY = _str("QWEN_API_KEY")
        self.QWEN_IMAGE_MODEL = _str("QWEN_IMAGE_MODEL", "qwen-image-2.0-pro")
        self.DASHSCOPE_BASE_URL = _str("DASHSCOPE_BASE_URL", "https://dashscope.aliyuncs.com/api/v1")
        self.QWEN_IMAGE_SIZE = _str("QWEN_IMAGE_SIZE", "1024*1024")
        self.QWEN_PROMPT_EXTEND = _bool("QWEN_PROMPT_EXTEND", False)

        # 兼容旧字段，避免示例代码里已有引用失效
        self.MODEL_API_KEY = _str("MODEL_API_KEY", self.DEEPSEEK_API_KEY)
        self.MODEL_BASE_URL = _str("MODEL_BASE_URL", self.DEEPSEEK_BASE_URL)
        self.MODEL_NAME = _str("MODEL_NAME", self.DEEPSEEK_MODEL)

if __name__ == "__main__":
    conf = Config()
    print(
        {
            "deepseek_model": conf.DEEPSEEK_MODEL,
            "deepseek_base_url": conf.DEEPSEEK_BASE_URL,
            "qwen_image_model": conf.QWEN_IMAGE_MODEL,
            "dashscope_base_url": conf.DASHSCOPE_BASE_URL,
        }
    )
