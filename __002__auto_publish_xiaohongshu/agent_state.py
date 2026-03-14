from typing import TypedDict, List


class AgentState(TypedDict):
    # 输入
    input: str
    image_count: int
    # 生成小红书标题和正文
    xiaohongshu_tcm_post_title: str
    xiaohongshu_tcm_post_content: str
    xiaohongshu_tcm_post_site: str
    # 生成小红书图片
    xiaohongshu_tcm_post_image_path_list: List[str]
    # 是否可以发布小红书
    is_can_publish_xiaohongshu: bool
    # 是否检测到真正发布成功
    publish_success: bool
    # 是否复用了缓存素材
    used_cache: bool
    # 输出
    output: str


