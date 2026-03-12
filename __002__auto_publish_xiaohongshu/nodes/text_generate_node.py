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
            "你是一个专门为小红书平台撰写旅行内容的文案助手。\n"
            "请根据用户提供的主题或需求，生成一条适合小红书发布的旅行类内容，要求包含：\n"
            "1. 吸引人的标题（title）：不超过19个中文字符，简短有吸引力\n"
            "2. 内容正文（content）：具有分享性和实用性，语气自然亲切，适合社交媒体，"
            "3. 获取用户输入中的地点(site): 一个城市或者一个省份，一个国家，或者一个景区，山脉，河流等。"
            "可以包含旅行攻略、目的地亮点、实用小贴士、个人体验等。\n"
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
    title, content, site = generate_xiaohongshu_tcm_post(user_input)

    state['xiaohongshu_tcm_post_title'] = title
    state['xiaohongshu_tcm_post_content'] = content
    state['xiaohongshu_tcm_post_site'] = site
    print(state)
    print("完成生成小红书标题和内容")
    return state


if __name__ == '__main__':
    text_generate_node({"input": "发个小红书，关于山东泰安。"})