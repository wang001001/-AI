"""
提供一个更适合直接运行的入口：
输入主题文本后，按顺序执行文案生成、图片生成、内容检查和自动发布。

若本地 LangGraph 环境可用，也保留构图与图执行能力；否则自动回退到顺序执行。
"""
import argparse
import sys

from __002__auto_publish_xiaohongshu.agent_state import AgentState
from __002__auto_publish_xiaohongshu.nodes.auto_publish_xiaohongshu_node import auto_publish_xiaohongshu_node
from __002__auto_publish_xiaohongshu.nodes.check_text_image_node import check_text_image_node
from __002__auto_publish_xiaohongshu.nodes.image_generate_node import image_generate_node
from __002__auto_publish_xiaohongshu.nodes.text_generate_node import text_generate_node
from common.langgraph_utils import output_pic_graph
from common.path_utils import get_file_path
from common.workflow_cache import get_cached_generation, save_cached_generation

try:
    from langgraph.graph import END, START, StateGraph
except ImportError as exc:
    END = START = StateGraph = None
    LANGGRAPH_IMPORT_ERROR = exc
else:
    LANGGRAPH_IMPORT_ERROR = None


def build_graph():
    if LANGGRAPH_IMPORT_ERROR is not None:
        raise RuntimeError(f"LangGraph 当前不可用: {LANGGRAPH_IMPORT_ERROR}")

    graph_builder = StateGraph(AgentState)
    graph_builder.add_node(text_generate_node.__name__, text_generate_node)
    graph_builder.add_node(image_generate_node.__name__, image_generate_node)
    graph_builder.add_node(check_text_image_node.__name__, check_text_image_node)
    graph_builder.add_node(auto_publish_xiaohongshu_node.__name__, auto_publish_xiaohongshu_node)

    graph_builder.add_edge(START, text_generate_node.__name__)
    graph_builder.add_edge(text_generate_node.__name__, image_generate_node.__name__)
    graph_builder.add_edge(image_generate_node.__name__, check_text_image_node.__name__)

    def check_control(state: AgentState):
        if state.get("is_can_publish_xiaohongshu"):
            return auto_publish_xiaohongshu_node.__name__
        return END

    graph_builder.add_conditional_edges(
        check_text_image_node.__name__,
        path=check_control,
        path_map={
            auto_publish_xiaohongshu_node.__name__: auto_publish_xiaohongshu_node.__name__,
            END: END,
        },
    )
    graph_builder.add_edge(auto_publish_xiaohongshu_node.__name__, END)
    return graph_builder.compile()


def export_graph_image():
    if LANGGRAPH_IMPORT_ERROR is not None:
        print(f"跳过流程图导出: {LANGGRAPH_IMPORT_ERROR}")
        return

    graph = build_graph()
    output_pic_graph(graph, get_file_path("__002__auto_publish_xiaohongshu/langgraph_auto_publish_xiaohongshu.png"))


def parse_args():
    parser = argparse.ArgumentParser(description="输入主题文本后，自动生成小红书文案、图片并发布。")
    parser.add_argument("text", nargs="*", help="想发布的小红书主题文本。")
    return parser.parse_args()


def configure_stdio():
    for stream_name in ("stdin", "stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream and hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")


def resolve_user_input() -> str:
    args = parse_args()
    if args.text:
        user_input = " ".join(args.text).strip()
    else:
        user_input = input("请输入想发布的小红书主题：").strip()
    if not user_input:
        raise ValueError("输入内容不能为空。")
    return user_input


def run_workflow_sequential(user_input: str):
    cached_generation = get_cached_generation(user_input)
    if cached_generation:
        print("命中文案与图片缓存，跳过重新生成。")
        state: AgentState = {
            "input": user_input,
            "xiaohongshu_tcm_post_title": cached_generation.get("xiaohongshu_tcm_post_title", ""),
            "xiaohongshu_tcm_post_content": cached_generation.get("xiaohongshu_tcm_post_content", ""),
            "xiaohongshu_tcm_post_site": cached_generation.get("xiaohongshu_tcm_post_site", ""),
            "xiaohongshu_tcm_post_image_path_list": cached_generation.get("xiaohongshu_tcm_post_image_path_list", []),
            "used_cache": True,
        }
        state = check_text_image_node(state)
    else:
        state: AgentState = {"input": user_input, "used_cache": False}
        for node in (
            text_generate_node,
            image_generate_node,
            check_text_image_node,
        ):
            state = node(state)

        if state.get("is_can_publish_xiaohongshu"):
            save_cached_generation(user_input, state)

    if state.get("is_can_publish_xiaohongshu"):
        state = auto_publish_xiaohongshu_node(state)
    return state


def run_workflow(user_input: str):
    return run_workflow_sequential(user_input)


def print_run_summary(result):
    print("\n运行结果摘要")
    print(f"标题: {result.get('xiaohongshu_tcm_post_title', '')}")
    print(f"地点: {result.get('xiaohongshu_tcm_post_site', '')}")
    print(f"图片: {result.get('xiaohongshu_tcm_post_image_path_list', [])}")
    print(f"发布状态: {result.get('output', '')}")


if __name__ == "__main__":
    configure_stdio()
    export_graph_image()
    try:
        user_input = resolve_user_input()
        result = run_workflow(user_input)
        print_run_summary(result)
    except KeyboardInterrupt:
        print("\n已取消本次运行。")
    except Exception as exc:
        print(f"\n运行失败: {exc}")
