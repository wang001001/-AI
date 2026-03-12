# 🚀 自动化小红书发布

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0+-green.svg)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Playwright](https://img.shields.io/badge/Playwright-1.40+-cyan.svg)](https://playwright.dev/)

**基于 LangGraph 的小红书自动化发布工作流**

</div>

---

## 📋 目录

- [项目概述](#-项目概述)
- [文件结构](#-文件结构)
- [环境依赖](#-环境依赖)
- [核心功能](#-核心功能)
- [使用方法](#-使用方法)
- [常见问题](#-常见问题)

---

## 📖 项目概述

本项目展示了如何基于 **LangGraph**（LangChain 的状态图工作流框架）构建一个完整的**小红书自动化发布系统**。

### 核心功能

| 功能 | 描述 | 关键技术 |
|------|------|----------|
| 🎨 **智能文案生成** | 根据用户需求自动生成小红书风格的标题和正文 | LLM、Pydantic 结构化输出 |
| 🖼️ **配图生成** | 根据文案内容生成匹配的配图 | 图片生成 API 集成 |
| ✅ **内容审核** | 检查文案长度、敏感词、图片尺寸等 | 规则引擎 |
| 📤 **自动发布** | 条件分支发布，审核通过后自动发布 | 自动化 API |

### 工作流图

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  text_generate  │───▶│ image_generate  │───▶│ check_control  │
│    (生成文案)    │    │    (生成配图)    │    │    (内容审核)    │
└─────────────────┘    └─────────────────┘    └────────┬────────┘
                                                        │
                              ┌─────────────────────────┼─────────────────────────┐
                              │                         │                         │
                              ▼                         ▼                         ▼
                    ┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
                    │ auto_publish   │        │      END       │        │      END       │
                    │   (发布笔记)    │        │   (审核失败)    │        │   (用户终止)    │
                    └─────────────────┘        └─────────────────┘        └─────────────────┘
```

---

## 📂 文件结构

```
.
├── __000__demo/                              # 基础示例
│   ├── langchain_outputparser_demo.py       # OutputParser 示例
│   └── tongyi_picture.py                     # 通义万相图片生成
│
├── __001__langgraph_translate_demo/          # 翻译工作流（学习参考）
│   ├── langgraph_translate.py                # 翻译实现
│   └── langgraph_translate.png               # 工作流图
│
├── __002__auto_publish_xiaohhongshu/         # ⭐ 小红书自动发布核心
│   ├── agent_state.py                        # 状态模型定义
│   ├── langgraph_auto_publish_xiaohongshu.py # 主工作流入口
│   └── nodes/
│       ├── text_generate_node.py             # 文案生成节点
│       ├── image_generate_node.py            # 图片生成节点
│       ├── check_text_image_node.py          # 内容审核节点
│       └── auto_publish_xiaohongshu_node.py  # 发布节点
│
├── common/                                    # 公共工具
│   ├── config.py                             # 配置
│   ├── llm.py                                # LLM 封装
│   ├── langgraph_utils.py                    # LangGraph 工具
│   ├── image_generate_utils.py               # 图片生成工具
│   └── path_utils.py                         # 路径工具
│
├── picture/                                   # 生成图片目录
├── cookie/                                    # Cookie 存储目录
├── test.py                                    # Playwright 抓取测试
├── requirements.txt                           # 依赖
└── .env                                       # 环境变量
```

---

## 🛠️ 环境依赖

```bash
# Python 3.10+
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install
```

### requirements.txt

```
playwright
langchain
langchain-openai
langgraph
pydantic
python-dotenv
```

---

## ⚡ 核心功能

### 1. 文案生成 (`text_generate_node`)

接收用户需求，调用 LLM 生成结构化文案：

```python
# 输入
{"input": "发个小红书，关于河南信阳的美食"}

# 输出
{
    "title": "信阳美食天花板！本地人私藏的必吃清单🍜",
    "content": "姐妹们！今天必须给你们分享信阳的宝藏美食...",
    "location": "河南信阳"
}
```

### 2. 图片生成 (`image_generate_node`)

根据文案内容生成匹配的配图（可接入 DALL·E、Stable Diffusion 等）。

### 3. 内容审核 (`check_text_image_node`)

检查是否符合发布规则：
- 文案长度（标题 20 字以内，正文 1000 字以内）
- 敏感词检测
- 图片尺寸要求

### 4. 自动发布 (`auto_publish_xiaohongshu_node`)

审核通过后自动调用发布 API。

---

## 🚦 使用方法

### 1. 配置环境变量

在 `.env` 文件中配置：

```env
OPENAI_API_KEY=your_api_key
ANTHROPIC_API_KEY=your_api_key
```

或在 `common/llm.py` 中直接配置。

### 2. 运行示例

```bash
# 小红书自动发布
python __002__auto_publish_xiaohongshu/langgraph_auto_publish_xiaohongshu.py

# 翻译工作流（参考）
python __001__langgraph_translate_demo/langgraph_translate.py

# 抓取 Cookies
python test.py
```

### 3. 自定义扩展

- 📝 修改 `text_generate_node` 的 Prompt 适配不同场景
- 🖼️ 在 `image_generate_node` 接入真实图片生成模型
- 📤 实现 `auto_publish_xiaohongshu_node` 的真实发布 API

---

## ❓ 常见问题

| 问题 | 解决方案 |
|------|----------|
| 运行 `test.py` 报错找不到浏览器 | 执行 `playwright install` 安装浏览器 |
| LLM 调用返回空 | 检查 API Key 是否有效 |
| StateGraph 报错节点未注册 | 确认已在 `build_graph()` 中添加所有节点 |
| 结构化输出解析失败 | 在 Prompt 中加入 "请严格遵守 JSON 格式" |
| 图片生成节点报错 | 当前为占位实现，需接入真实 API |

---

## 🎯 项目目标

- **自动化**：减少重复性工作，专注内容创意
- **模块化**：基于 LangGraph 便于扩展新功能
- **可定制**：轻松适配其他社交平台（微博、抖音等）

---

## 📄 License

MIT License

---

<div align="center">

Made with ❤️ using LangGraph

</div>
