from __002__auto_publish_xiaohongshu.agent_state import AgentState

from pydantic import BaseModel, Field
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.output_parsers import PydanticOutputParser, JsonOutputParser

from common.llm import my_llm


class XiaohongshuTCMPostOutput(BaseModel):
    title: str = Field(description="小红书标题")
    content: str = Field(description="小红书内容")
    site: str = Field(description="小红书内容所在的地点")


# # 拼接完整答案
def generate_xiaohongshu_tcm_post(user_input: str):
    parser = JsonOutputParser(pydantic_object=XiaohongshuTCMPostOutput)
    format_instructions = parser.get_format_instructions()

    messages = [
        SystemMessage(content=(
            "你是一个专门为小红书平台撰写图文笔记的文案助手。\n"
            "请根据用户提供的主题或需求，生成一条适合小红书发布的内容，要求包含：\n"
            "1. 吸引人的标题（title）：不超过18个中文字符，简短有吸引力\n"
            "2. 内容正文（content）：控制在 180 到 320 个中文字符，信息密度高，适合直接发布\n"
            "3. 地点或场景（site）：如果用户提到了城市、国家、景区、平台、行业或具体场景，就提炼出来；如果没有，就写“无明确地点”\n"
            "正文风格要求：自然、口语化、有干货，允许带少量 emoji 和 2 到 4 个相关标签。\n"
            "请你严格按照以下格式返回结果：\n"
            f"{format_instructions}"
        )),
        HumanMessage(content=user_input)
    ]
    raw_output = my_llm.invoke(messages).content
    result_dict = parser.parse(raw_output)
    return result_dict.get("title", ""), result_dict.get("content", ""), result_dict.get("site", "")

def text_generate_node(state: AgentState):
    """根据用户输入生成中医养生类的小红书文案（包括标题、内容、策略）"""
    print("开始生成小红书标题和内容")
    user_input = state.get('input', "")
    try:
        title, content, site = generate_xiaohongshu_tcm_post(user_input)
    except Exception as e:
        state['xiaohongshu_tcm_post_title'] = ""
        state['xiaohongshu_tcm_post_content'] = ""
        state['xiaohongshu_tcm_post_site'] = ""
        state['output'] = f"文案生成失败: {e}"
        print(state['output'])
        return state

    state['xiaohongshu_tcm_post_title'] = title
    state['xiaohongshu_tcm_post_content'] = content
    state['xiaohongshu_tcm_post_site'] = site
    print(state)
    print("完成生成小红书标题和内容")
    return state


if __name__ == '__main__':
    text_generate_node({"input": "发个小红书，关于山东泰安。"})
