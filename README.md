# LangGraph Course 27 – 实战案例合集

## 目录
1. 项目概述  
2. 文件结构  
3. 环境依赖  
4. 关键示例  
   - 01️⃣ 语言翻译 Demo (`__001__langgraph_translate_demo`)  
   - 02️⃣ 小红书自动发布 Demo (`__002__auto_publish_xiaohongshu`)  
   - 03️⃣ 浏览器 Cookie/LocalStorage 抽取 (`test.py`)  
5. 使用方法  
6. 常见问题  

## 1️⃣ 项目概述
本项目是 **LangGraph**（基于 LangChain 的状态图工作流）课程第 27 章节的实战代码合集，展示了如何通过 **StateGraph** 把多个 LLM 交互节点串联为完整的业务流程。  
主要演示两大应用场景：

| 场景 | 目标 | 关键技术 |
|------|------|----------|
| **语言翻译** | 根据用户输入自动识别意图（翻译 vs 普通问答），提取待翻译句子并完成中英互译 | `StateGraph`、意图分类、文本抽取、LLM 调用 |
| **小红书自动发布** | 从用户需求自动生成旅行文案 → 生成配图 → 检查可发布性 → 条件分支发布 | `StateGraph`、结构化输出（JSON/Pydantic）、图片生成、条件边、自动化发布 |
| **浏览器数据抽取** | 使用 Playwright 抓取 XHS（小红书）页面的 Cookies 与 LocalStorage，输出为 JSON | Playwright、跨平台浏览器自动化 |

## 2️⃣ 文件结构

```
langgraph_course_27/
│
├─ __000__demo/
│   ├─ langchain_outputparser_demo.py
│   └─ tongyi_picture.py
│
├─ __001__langgraph_translate_demo/
│   ├─ langgraph_translate.py       # 翻译工作流实现
│   └─ langgraph_translate.png     # 工作流可视化图
│
├─ __002__auto_publish_xiaohongshu/
│   ├─ agent_state.py               # 状态模型定义
│   ├─ langgraph_auto_publish_xiaohongshu.py  # 主工作流入口
│   ├─ __002__auto_publish_xiaohongshu/
│   │   └─ (可能的资源文件)
│   └─ nodes/
│       ├─ text_generate_node.py                # 生成文案（结构化 JSON）
│       ├─ image_generate_node.py               # 生成配图（占位实现）
│       ├─ check_text_image_node.py             # 检查文案/图片合法性
│       └─ auto_publish_xiaohongshu_node.py     # 调用发布接口（示例）
│
├─ test.py                                 # Playwright 抓取 cookies/localStorage
├─ requirements.txt                         # 项目依赖
└─ common/                                 # 公共工具（LLM 包装、路径、绘图等）
```

> **备注**：项目根目录只有 `requirements.txt` 这一个纯文本文件，所有业务代码均在子目录中组织。

## 3️⃣ 环境依赖

```text
# requirements.txt
playwright
langchain
langchain-openai
langgraph
pydantic
```

运行前请确保已安装 `playwright` 浏览器（`playwright install`）并配置好 OpenAI/Claude API Key（`common/llm.py` 中的 `my_llm`）。

## 4️⃣ 关键示例

### 4.1 语言翻译 Demo (`__001__langgraph_translate_demo`)

**核心概念**
- **意图判断节点**：使用 LLM 判断输入是「翻译」还是「普通问答」  
- **翻译句子抽取节点**：自动识别语言并抽取待翻译文本  
- **翻译节点**：中英互译，仅返回译文  
- **问答节点**：普通问答的 fallback  

**使用方式（示例）**

```python
from __001__langgraph_translate_demo.langgraph_translate import graph

# 翻译示例
result = graph.invoke({"input": "请把这句话翻译成英文：找工作真快乐啊！"})
print(result["output"])   # => "Finding a job is truly joyful!"

# 问答示例
result = graph.invoke({"input": "请介绍下清朝的皇帝。"})
print(result["output"])   # => "清朝历经十位皇帝，分别是…"
```

**可视化**：`langgraph_translate.png` 展示了节点之间的有向图。

### 4.2 小红书自动发布 Demo (`__002__auto_publish_xiaohongshu`)

**工作流概览**

1. **text_generate_node**  
   - 接收用户需求（如 “发个小红书，关于河南信阳”。）  
   - 调用 LLM 生成结构化文案（标题、正文、地点），返回 JSON。  

2. **image_generate_node**  
   - 根据文案生成配图（示例代码占位，可自行接入 Stable Diffusion / DALL·E）。  

3. **check_text_image_node**  
   - 校验文案与图片是否符合发布规则（长度、敏感词、图片尺寸等）。  

4. **条件分支** (`check_control`)  
   - 若 `is_can_publish_xiaohongshu` 为 `True` → 进入 `auto_publish_xiaohongshu_node`，否则结束。  

5. **auto_publish_xiaohongshu_node**  
   - 调用小红书发布 API（示例中为伪实现），返回 `output`。  

**运行示例**

```python
from __002__auto_publish_xiaohongshu.langgraph_auto_publish_xiaohongshu import graph

result = graph.invoke({"input": "发个小红书，关于河南信阳。"})
print("最终 output:", result.get("output"))
```

**可视化**：`langgraph_auto_publish_xiaohongshu.png`（在 `__002__auto_publish_xiaohongshu` 目录下生成）。

### 4.3 浏览器数据抽取 (`test.py`)

使用 **Playwright** 打开指定 URL，自动绕过自动化检测，提取：

- **Cookies**（完整字段，支持持久化）  
- **LocalStorage**（键值对列表）  

结果保存为 `cookies.json`，结构示例：

```json
{
  "cookies": [...],
  "origins": [
    {
      "origin": "https://www.xiaohongshu.com/explore",
      "localStorage": [...]
    }
  ]
}
```

可作为后续 **登录态复用** 或 **爬虫** 的输入。

## 5️⃣ 使用方法

1. **创建虚拟环境**（推荐）  

   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   playwright install
   ```

2. **配置 LLM API**  
   在 `common/llm.py` 中填写对应的 `OPENAI_API_KEY` 或 `ANTHROPIC_API_KEY`。

3. **运行示例**  

   ```bash
   python __001__langgraph_translate_demo/langgraph_translate.py   # 直接跑 __main__ 示例
   python __002__auto_publish_xiaohongshu/langgraph_auto_publish_xiaohongshu.py
   python test.py   # 抓取 cookies
   ```

4. **自定义**  
   - 替换 `text_generate_node` 的系统提示，以适配不同文案场景。  
   - 在 `image_generate_node` 中接入真实的图片生成模型。  
   - 实现 `auto_publish_xiaohongshu_node` 的真实发布 API（官方 SDK / HTTP）。

## 6️⃣ 常见问题

| 问题 | 解决方案 |
|------|----------|
| **运行 `test.py` 报错找不到浏览器** | 确认已执行 `playwright install`，或手动安装 Chrome/Chromium。 |
| **LLM 调用返回空字符串** | 检查 API Key 是否有效、配额是否耗尽；确保 `my_llm` 的 `temperature`、`model` 参数设置合理。 |
| **`StateGraph` 报错节点未注册** | 确认在 `build_graph()` 中已 `add_node` 所有自定义函数，并使用 `__name__` 传递。 |
| **结构化输出解析失败** | 确认 LLM 按 `JsonOutputParser` 的格式指示返回 JSON；可在 Prompt 中加入 “请严格遵守 JSON 格式”。 |
| **图片生成节点报错** | 当前占位实现仅返回固定路径；若接入真实模型，请确保返回值符合 `state["image_path"]` 键的约定。 |

### 🎯 项目目标

- **教学**：通过完整的工作流示例，帮助学习者快速掌握 LangGraph 的节点定义、条件边与图的可视化。  
- **实战**：展示如何把 LLM 与外部系统（浏览器、社交平台）组合，实现端到端的内容生成与自动化发布。  
- **可扩展**：代码结构遵循 **模块化 + Pydantic**，便于后续添加新节点（如情感分析、内容审查）或迁移到其他平台（微博、抖音等）。  

祝学习愉快，玩转 LangGraph！
