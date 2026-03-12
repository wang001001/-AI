from typing import TypedDict, Literal
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END, START
from langchain_core.messages import SystemMessage, HumanMessage

from common.langgraph_utils import output_pic_graph
from common.llm import my_llm

# ========== 2) 定义状态 ==========
class AgentState(dict):
    # 输入
    input: str
    # 是否是翻译
    is_translate_or_not: bool
    # 要翻译的句子
    translate_sentence:str
    # 翻译结果
    translate_result: str
    # QA结果
    qa_result: str
    # 输出
    output: str


def identify_intent_node(state: AgentState) -> AgentState:
    """判断用户输入是翻译文章还是普通回答"""
    print("意图判断节点")
    input = state['input']
    messages = [
        SystemMessage(content=(
            "你是一个意图分类助手，用来判断用户输入是'翻译任务'还是'普通回答任务'。\n"
            "翻译任务的特征：用户明确要求翻译文章、句子、单词，或要求将中文翻译成英文/英文翻译成中文。\n"
            "普通回答任务的特征：用户是直接提问、咨询信息、讨论话题，而不是要求翻译。\n"
            "请你只回答：翻译 或 普通回答，不要补充其他内容。"
        )),
        HumanMessage(content=input)
    ]

    response = my_llm.invoke(messages).content.strip()

    if "翻译" in response:
        state['is_translate_or_not'] = True
    else:
        state['is_translate_or_not'] = False

    return state

def extract_translate_sentence_node(state: AgentState) -> AgentState:
    """提取翻译句子"""
    print("提取翻译句子节点")
    input = state['input']
    prompot = (
        "你是提取句子助手。请先自动识别语言，然后提取待翻译的句子。"
        "请将待翻译的句子提取出来，并输出。"
        "请不要输出其他内容，也不要进行翻译。\n"
        f"待翻译内容：{input}"
    )
    result = my_llm.invoke([HumanMessage(content=prompot)]).content
    state['translate_sentence'] = result
    return state

def translate_node(state: AgentState) -> AgentState:
    """翻译节点"""
    print("翻译节点")
    translate_sentence = state["translate_sentence"]
    prompt = (
        "你是翻译助手。请先自动识别语言，然后在中文与英文之间互译。"
        "只输出译文本身，不要额外解释。\n"
        f"待翻译内容：{translate_sentence}"
    )
    result = my_llm.invoke([HumanMessage(content=prompt)]).content
    state['translate_result'] = result
    state['output'] = result
    # 按你的状态定义回写
    return state


def qa_node(state: AgentState) -> AgentState:
    """QA节点"""
    print("QA节点")
    qa_sentence = state["input"]
    prompt = (
        "你是一个问答助手，请回答问题。"
        "请使用中文回答。\n"
        f"问题：{qa_sentence}"
    )
    result = my_llm.invoke([HumanMessage(content=prompt)]).content
    state['qa_result'] = result
    state['output'] = result
    # 按你的状态定义回写
    return state

def build_graph():
    graph_builder = StateGraph(AgentState)
    # 添加四个节点
    graph_builder.add_node(identify_intent_node.__name__, identify_intent_node)
    graph_builder.add_node(extract_translate_sentence_node.__name__, extract_translate_sentence_node)
    graph_builder.add_node(translate_node.__name__, translate_node)
    graph_builder.add_node(qa_node.__name__, qa_node)
    # 添加边
    graph_builder.add_edge(START, identify_intent_node.__name__)
    def identity_intent_control(state: AgentState):
        if state['is_translate_or_not']:
            return extract_translate_sentence_node.__name__
        else:
            return qa_node.__name__
    graph_builder.add_conditional_edges(identify_intent_node.__name__, path=identity_intent_control,
                                        path_map={
        extract_translate_sentence_node.__name__: extract_translate_sentence_node.__name__,
        qa_node.__name__: qa_node.__name__
    })
    graph_builder.add_edge(extract_translate_sentence_node.__name__, translate_node.__name__)
    graph_builder.add_edge(qa_node.__name__, END)
    graph_builder.add_edge(translate_node.__name__, END)
    graph = graph_builder.compile()
    return graph


graph = build_graph()


output_pic_graph(graph, "langgraph_translate.png")

if __name__ == '__main__':
    input = "请把这句话翻译成英文：找工作真快乐啊！"
    result = graph.invoke({'input': input})
    print(result)
    print(result["output"])


    input = "请介绍下清朝的皇帝。"
    result = graph.invoke({'input': input})
    # print(result)
    print(result["output"])