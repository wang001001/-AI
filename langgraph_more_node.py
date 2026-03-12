from langgraph.constants import START, END
from langgraph.graph import StateGraph

from agent_state import AgentState
from nodes.text_generate_node import text_generate_node
from nodes.image_generate_node import image_generate_node
from nodes.check_text_image_node import check_text_image_node
from nodes.auto_publish_xiaohongshu_node import publish_node as auto_publish_xiaohongshu_node


def build_graph():
    graph_builder = StateGraph(AgentState)

    # 添加节点
    graph_builder.add_node(text_generate_node.__name__, text_generate_node)
    graph_builder.add_node(image_generate_node.__name__, image_generate_node)
    graph_builder.add_node(check_text_image_node.__name__, check_text_image_node)
    graph_builder.add_node(auto_publish_xiaohongshu_node.__name__, auto_publish_xiahongshu_node)

    # 添加顺序边
    graph_builder.add_edge(START, text_generate_node.__name__)
    graph_builder.add_edge(text_generate_node.__name__, image_generate_node.__name__)
    graph_builder.add_edge(image_generate_node.__name__, check_text_image_node.__name__)

    # 条件分支：校验通过则发布，否则结束
    def check_text_image_condition(state: AgentState):
        if state.get("is_can_publish_xiaohongshu", False):
            return auto_publish_xiaohongshu_node.__name__
        else:
            return END

    # 添加条件边
    graph_builder.add_conditional_edge(check_text_image_node.__name__, check_text_image_condition)
    graph_builder.add_edge(auto_publish_xiaohongshu_node.__name__, END)

    graph = graph_builder.compile()
    return graph


if __name__ == "__main__":
    user_input = "我想去南京。"
    graph = build_graph()
    result = graph.invoke({"input": user_input})
    print(result)
