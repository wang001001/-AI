import datetime
import os

from __002__auto_publish_xiaohongshu.agent_state import AgentState
from common.image_generate_utils import generate_and_download_image
from common.path_utils import get_file_path

def sanitize_title_for_filename(title: str) -> str:
    """
    将标题字符串清洗成适合作为文件名的格式（去除不合法字符，只保留前max_length个字符）

    :param title: 原始标题
    :param max_length: 截取的最大字符数
    :return: 清洗后的文件名部分
    """
    # 获取现在的时间
    now = datetime.datetime.now()
    # 格式化时间
    time_str = now.strftime("%Y%m%d%H%M%S")
    return time_str + title[:5] + ".png"

def generate_jimeng_prompt(title: str, content: str, site: str) -> str:
    content_summary = (content or "")[:120]
    return (
        f"请生成一张适合小红书图文封面的高质量图片。"
        f"主题：{title}。"
        f"核心内容：{content_summary}。"
        f"场景或地点：{site or '无明确地点'}。"
        f"要求：主体明确，风格贴合主题，构图简洁，画面干净高级，适合社交媒体封面。"
        f"图片中不能有任何文字、水印或 Logo。"
    )


def xiaohongshu_image_generator(title, content, site, image_count: int):
    # 建了一个文件夹，用于保存图片
    os.makedirs(get_file_path("picture"), exist_ok=True)

    image_paths = []
    for index in range(image_count):
        prompt = (
            f"{generate_jimeng_prompt(title, content, site)}"
            f" 第 {index + 1} 张图请使用不同的构图、主体位置或景别，保持同主题一致性。"
        )
        file_name = sanitize_title_for_filename(f"{title}_{index + 1}")
        output_path = os.path.join(get_file_path("picture"), file_name)
        image_path = generate_and_download_image(prompt, output_path)
        if image_path:
            image_paths.append(image_path)
    return image_paths

def image_generate_node(state: AgentState):
    """根据标题和内容生成中医养生风格的小红书配图"""
    try:
        print("开始生成小红书图片生成")
        title = state.get('xiaohongshu_tcm_post_title')
        content = state.get('xiaohongshu_tcm_post_content')
        site = state.get('xiaohongshu_tcm_post_site')
        image_count = max(1, min(int(state.get('image_count', 1) or 1), 5))

        image_paths = xiaohongshu_image_generator(title, content, site, image_count)

        if image_paths:
            state['xiaohongshu_tcm_post_image_path_list'] = image_paths
            print(f"图片生成成功，共 {len(image_paths)} 张")
            print("完成生成小红书图片生成")
        else:
            state['xiaohongshu_tcm_post_image_path_list'] = []
            state['output'] = "图片生成失败"
            print("图片生成失败")
    except Exception as e:
        import traceback
        traceback.print_exc()
        state['xiaohongshu_tcm_post_image_path_list'] = []
        state['output'] = f"图片生成异常: {e}"
    return state

if __name__ == '__main__':
    image_generate_node({"xiaohongshu_tcm_post_site":"沧州", "xiaohongshu_tcm_post_title":"沧州是个好地方"})
