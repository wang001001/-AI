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
    return (
        f"一幅围绕旅行探索主题创作的高质量图像，"
        f"画面展现与标题内容相关的旅行场景，如自然风光、城市街景、异国风情或户外探险，"
        f"构图中可以包含人物、交通工具、建筑或自然景观，"
        f"整体氛围充满冒险、自由与美好假期的感觉，色调明亮或富有层次，"
        f"背景可以是山川、海滩、森林、古城、夜景等，"
        f"表达放松、探索、享受生活的情绪。"
        f"图片描述地址为:{site}。"
        f"图片中不能有任何文字。"
        f"允许写实艺术风格，但需保证画面和谐美观、细节丰富。"
    )


def xiaohongshu_image_generator(title, content, site):
    # 生成提示词
    prompt = generate_jimeng_prompt(title, content, site)

    # 建了一个文件夹，用于保存图片
    os.makedirs(get_file_path("picture"), exist_ok=True)
    file_name = sanitize_title_for_filename(title)
    output_path = os.path.join(get_file_path("picture"), file_name)

    # 生成图片并且下载
    generate_and_download_image(prompt, output_path)
    return output_path

def image_generate_node(state: AgentState):
    """根据标题和内容生成中医养生风格的小红书配图"""
    try:
        print("开始生成小红书图片生成")
        title = state.get('xiaohongshu_tcm_post_title')
        content = state.get('xiaohongshu_tcm_post_content')
        site = state.get('xiaohongshu_tcm_post_site')

        image_path = xiaohongshu_image_generator(title, content, site)

        state['xiaohongshu_tcm_post_image_path_list'] = [image_path]
        print(f"图片生成成功: {image_path}")
        print("完成生成小红书图片生成")
    except Exception as e:
        import traceback
        traceback.print_exc()
    return state

if __name__ == '__main__':
    image_generate_node({"xiaohongshu_tcm_post_site":"沧州", "xiaohongshu_tcm_post_title":"沧州是个好地方"})