"""
仿照 __001__langgraph_translate_demo 的 StateGraph 写法，
将 002 下的各 node 串成图：文案生成 → 图片生成 → 检查 → 条件分支 → 发布/结束。
"""
from langgraph.graph import StateGraph, END, START

from __002__auto_publish_xiaohongshu.agent_state import AgentState
from __002__auto_publish_xiaohongshu.nodes.text_generate_node import text_generate_node
from __002__auto_publish_xiaohongshu.nodes.image_generate_node import image_generate_node
from __002__auto_publish_xiaohongshu.nodes.check_text_image_node import check_text_image_node
from __002__auto_publish_xiaohongshu.nodes.auto_publish_xiaohongshu_node import auto_publish_xiaohongshu_node

from common.langgraph_utils import output_pic_graph
from common.path_utils import get_file_path


def build_graph():
    graph_builder = StateGraph(AgentState)
    # 添加节点
    graph_builder.add_node(text_generate_node.__name__, text_generate_node)
    graph_builder.add_node(image_generate_node.__name__, image_generate_node)
    graph_builder.add_node(check_text_image_node.__name__, check_text_image_node)
    graph_builder.add_node(auto_publish_xiaohongshu_node.__name__, auto_publish_xiaohongshu_node)
    # 添加边
    graph_builder.add_edge(START, text_generate_node.__name__)
    graph_builder.add_edge(text_generate_node.__name__, image_generate_node.__name__)
    graph_builder.add_edge(image_generate_node.__name__, check_text_image_node.__name__)

    def check_control(state: AgentState):
        if state.get("is_can_publish_xiaohongshu"):
            return auto_publish_xiaohongshu_node.__name__
        return END

    graph_builder.add_conditional_edges(check_text_image_node.__name__, path=check_control,
        path_map={
            auto_publish_xiaohongshu_node.__name__: auto_publish_xiaohongshu_node.__name__,
            END: END,
        }
    )
    graph_builder.add_edge(auto_publish_xiaohongshu_node.__name__, END)

    return graph_builder.compile()


graph = build_graph()
output_pic_graph(graph, get_file_path("__002__auto_publish_xiaohongshu/langgraph_auto_publish_xiaohongshu.png"))

if __name__ == "__main__":
    result = graph.invoke({"input": "发个小红书，关于河南信阳。"})
    print("最终 output:", result.get("output"))
