import os
import requests
import dashscope
from dashscope import MultiModalConversation

from common.config import Config
from common.path_utils import get_file_path

conf = Config()

# 以下为北京地域url，若使用新加坡地域的模型，需将url替换为：https://dashscope-intl.aliyuncs.com/api/v1
dashscope.base_http_api_url = conf.DASHSCOPE_BASE_URL

# 默认负面提示，用于提升画质
DEFAULT_NEGATIVE_PROMPT = (
    "低分辨率，低画质，肢体畸形，手指畸形，画面过饱和，蜡像感，人脸无细节，"
    "过度光滑，画面具有AI感。构图混乱。文字模糊，扭曲。"
)


def generate_and_download_image(
    prompt: str,
    save_path: str,
    *,
    size: str = "1024*1024",
    negative_prompt: str = DEFAULT_NEGATIVE_PROMPT,
    api_key: str | None = None,
) -> str | None:
    """
    根据提示词调用通义画图 API 生成图片，并下载到指定路径。

    :param prompt: 画图提示词，如 "画一个小鹿的图片。"
    :param save_path: 图片保存路径，可为相对路径或绝对路径，内部会转为绝对路径后保存
    :param size: 图片尺寸，默认 1024*1024
    :param negative_prompt: 负面提示词，用于避免低质量元素
    :param api_key: API Key，不传则使用 Config 中的 QWEN_API_KEY
    :return: 成功返回保存的绝对路径，失败返回 None
    """
    key = api_key or conf.QWEN_API_KEY
    if not key:
        print("错误：未配置 QWEN_API_KEY")
        return None

    messages = [
        {
            "role": "user",
            "content": [{"text": prompt}],
        }
    ]

    response = MultiModalConversation.call(
        api_key=key,
        model="qwen-image-2.0-pro",
        messages=messages,
        result_format="message",
        stream=False,
        watermark=False,
        prompt_extend=True,
        negative_prompt=negative_prompt,
        size=size,
    )

    if response.status_code != 200:
        print(f"API 调用失败 - 返回码：{response.status_code}")
        print(f"错误码：{response.code}，错误信息：{response.message}")
        return None

    # 从响应中取出图片 URL（兼容 dict / 对象两种返回格式）
    try:
        output = response.output
        choices = getattr(output, "choices", None) or output.get("choices") or []
        if not choices:
            print("响应中无 choices")
            return None
        c0 = choices[0]
        message = getattr(c0, "message", None) or c0.get("message") or {}
        content = getattr(message, "content", None) or message.get("content") or []
        if not content:
            print("响应中无 content")
            return None
        first = content[0]
        image_url = getattr(first, "image", None) or first.get("image")
    except (IndexError, KeyError, TypeError, AttributeError) as e:
        print(f"解析响应失败：{e}")
        return None

    if not image_url:
        print("图片 URL 为空")
        return None

    # 确保目录存在
    save_dir = os.path.dirname(save_path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)

    # 下载图片
    try:
        resp = requests.get(image_url, timeout=60)
        resp.raise_for_status()
        with open(save_path, "wb") as f:
            f.write(resp.content)
        print(f"图片已保存：{save_path}")
        return save_path
    except requests.RequestException as e:
        print(f"下载图片失败：{e}")
        return None
    except OSError as e:
        print(f"写入文件失败：{e}")
        return None


if __name__ == "__main__":
    # 示例：输入提示词和保存路径即可生成并下载
    generate_and_download_image(
        prompt="画一个美女的图片。",
        save_path=get_file_path("__000__demo/output/deer.png"),
    )
