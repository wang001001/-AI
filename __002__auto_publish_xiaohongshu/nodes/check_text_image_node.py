import os.path

from __002__auto_publish_xiaohongshu.agent_state import AgentState


def check_text_image_node(state: AgentState):
    """检查是否可以发布小红书"""
    title = state.get("xiaohongshu_tcm_post_title", "")
    content = state.get("xiaohongshu_tcm_post_content", "")
    image_path_list = state.get("xiaohongshu_tcm_post_image_path_list", [])
    state["is_can_publish_xiaohongshu"] = True
    if not title:
        state["is_can_publish_xiaohongshu"] = False
        state["output"] = "发布小红书失败，标题缺失！"
    if not content:
        state["is_can_publish_xiaohongshu"] = False
        state["output"] = "发布小红书失败，内容缺失！"
    if not image_path_list:
        state["is_can_publish_xiaohongshu"] = False
        state["output"] = "发布小红书失败，图片缺失！"
    image_path = image_path_list[0]
    if not os.path.exists(image_path):
        state["is_can_publish_xiaohongshu"] = False
        state["output"] = "发布小红书失败，图片不存在！"
    return state