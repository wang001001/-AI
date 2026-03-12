import os.path
from agent_state import AgentState
import os
from agent_state import AgentState

def check_text_image_node(state: AgentState):
    """检查是否可以发布小红书"""
    title = state.get("xiaohongshu_tcm_post_title", "")
    content = state.get("xiaohongshu_tcm_post_content", "")
    image_path_list = state.get("xiaohongshu_tcm_post_image_path_list", [])

    # 初始默认可以发布
    state["is_can_publish_xiaohongshu"] = True
    state["output"] = ""

    if not title:
        state["is_can_publish_xiaohongshu"] = False
        state["output"] = "发布小红书失败，标题缺失！"
    if not content:
        state["is_can_publish_xiaohongshu"] = False
        state["output"] = "发布小红书失败，内容缺失！"
    if not image_path_list:
        state["is_can_publish_xiahongshu"] = False
        state["output"] = "发布小红书失败，图片缺失！"
    else:
        image_path = image_path_list[0]
        if not os.path.exists(image_path):
            state["is_can_publish_xiaohongshu"] = False
            state["output"] = "发布小红书失败，图片不存在！"
    return state
