import json
import os
from dotenv import load_dotenv

from common.path_utils import get_file_path

# load_dotenv(get_file_path(".env"))
load_dotenv(rf"D:\my_duyi_project_dir\my_env/.env_tongyi_mian")

def _int(key: str, default: int = 0) -> int:
    val = os.getenv(key)
    return int(val) if val is not None else default


def _str(key: str, default: str = "") -> str:
    return os.getenv(key) or default


class Config:
    def __init__(self):
        # 大模型相关
        self.MODEL_API_KEY = _str("MODEL_API_KEY")
        self.MODEL_BASE_URL = _str("MODEL_BASE_URL")
        self.MODEL_NAME = _str("MODEL_NAME")

if __name__ == "__main__":
    conf = Config()
    print(conf.BERT_BASE_PATH)
