# 小红书自动发布项目

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-Web%20UI-009688.svg)](https://fastapi.tiangolo.com/)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-cyan.svg)](https://playwright.dev/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

输入主题文本，自动生成小红书文案、配图，并通过浏览器自动发布。

</div>

## 项目简介

这是一个面向小红书图文发布的自动化项目，当前已经支持：

- 前端页面输入主题文本
- 后端自动调用大模型生成小红书文案
- 自动调用图片模型生成配图
- 自动打开小红书创作页并上传图文
- 首次登录后复用本地登录态
- 同一主题短时间内复用缓存文案和图片，减少重复生成耗时

项目目前的默认模型组合是：

- 文案生成：DeepSeek
- 图片生成：Qwen
- 自动发布：Playwright 驱动小红书创作页

## 当前能力

### 1. 前端输入发布

项目新增了一个网页入口，用户打开页面后，只需要输入主题文本并点击按钮，就会触发整条发布流程。

页面会展示：

- 当前是否已有小红书登录态
- 执行中状态
- 生成后的标题、正文、地点
- 配图预览
- 发布结果

### 2. 文案生成

文案节点会根据输入主题生成：

- 标题
- 正文
- 场景或地点

当前 prompt 已改成更通用的小红书图文风格，不再只适配旅行内容。

### 3. 图片生成

图片节点会根据文案主题、正文摘要和场景生成适合做小红书封面的图片。

### 4. 自动发布

发布节点会：

- 打开小红书创作页
- 检测或复用登录态
- 上传图片
- 填充标题和正文
- 等待图片上传稳定后再点击发布
- 等待真正的发布接口响应，而不是只看页面文案

### 5. 缓存提速

对于相同输入，项目会缓存最近一次生成的文案和图片。

这样在短时间内重复发布同一个主题时，可以跳过最慢的两步：

- 文案生成
- 图片生成

## 项目结构

```text
.
├── __000__demo/                              # 早期示例代码
├── __001__langgraph_translate_demo/          # LangGraph 学习示例
├── __002__auto_publish_xiaohongshu/          # 小红书自动发布核心流程
│   ├── agent_state.py
│   ├── langgraph_auto_publish_xiaohongshu.py
│   └── nodes/
│       ├── text_generate_node.py
│       ├── image_generate_node.py
│       ├── check_text_image_node.py
│       └── auto_publish_xiaohongshu_node.py
├── common/                                   # 公共配置、模型和缓存工具
│   ├── config.py
│   ├── llm.py
│   ├── image_generate_utils.py
│   ├── workflow_cache.py
│   ├── langgraph_utils.py
│   └── path_utils.py
├── web/                                      # 前端页面
│   ├── index.html
│   └── assets/
│       ├── app.js
│       └── styles.css
├── webapp.py                                 # FastAPI 服务入口
├── start_web.ps1                             # 一键启动脚本
├── picture/                                  # 生成图片目录
├── cookie/                                   # 登录态和工作流缓存
├── test.py                                   # Playwright 调试脚本
├── requirements.txt
└── .env.example
```

## 环境准备

### 1. Python

建议使用 Python 3.10 及以上版本。

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 安装 Playwright 浏览器

```bash
playwright install chromium
```

## 配置方式

项目使用仓库根目录下的 `.env` 配置文件。

你可以先参考 [.env.example](/D:/My_preprodict/codex_myOnePreproject/.env.example)：

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
DEEPSEEK_BASE_URL=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

QWEN_API_KEY=your_qwen_api_key
QWEN_IMAGE_MODEL=qwen-image-2.0-pro
DASHSCOPE_BASE_URL=https://dashscope.aliyuncs.com/api/v1
```

可选配置：

```env
QWEN_IMAGE_SIZE=1024*1024
QWEN_PROMPT_EXTEND=false
```

## 使用方式

### 方式一：启动前端页面

PowerShell：

```powershell
.\start_web.ps1
```

或者：

```powershell
D:\AnaConda\python.exe -m uvicorn webapp:app --host 127.0.0.1 --port 8000 --reload
```

启动后打开：

[http://127.0.0.1:8000](http://127.0.0.1:8000)

然后在页面中输入主题文本，例如：

```text
请发一个关于TK跨境电商的小红书
```

### 方式二：命令行直接运行

```bash
python __002__auto_publish_xiaohongshu/langgraph_auto_publish_xiaohongshu.py "请发一个关于TK跨境电商的小红书"
```

或者直接运行后手动输入：

```bash
python __002__auto_publish_xiaohongshu/langgraph_auto_publish_xiaohongshu.py
```

## 首次发布说明

首次真实发布时，程序会打开浏览器并进入小红书创作页。

你需要：

- 在浏览器中完成小红书登录
- 等待页面自动继续

登录态会保存到：

```text
cookie/xiaohongshu_state.json
```

后续发布会直接复用，不需要重复登录。

## 项目发布流程

当前默认顺序是：

1. 输入主题文本
2. 生成文案
3. 生成图片
4. 校验标题、正文、图片
5. 打开小红书创作页
6. 上传图片并填充图文
7. 等待上传稳定后点击发布
8. 检测真正的发布接口响应

## 重要说明

### 1. 页面“发布成功”现在如何判断

项目不再只根据页面上是否出现“成功”字样判断。

现在会优先等待真正的发布接口响应，并解析接口返回结果，再决定是否真正发布成功。

### 2. 为什么有时会感觉慢

最耗时的步骤通常是：

- 大模型生成文案
- 图片模型生成图片
- 小红书页面上传图片

当前已经做了两类优化：

- 同一主题 1 小时内复用缓存文案与图片
- 发布前等待上传稳定，减少“过早点击导致失败后重试”

### 3. 为什么仍然可能失败

这是浏览器自动化项目，不是官方开放平台直连，所以仍然会受这些因素影响：

- 小红书页面结构变化
- 登录态失效
- 图片仍在处理
- 页面校验规则变化
- 网络波动

## 常见问题

### 运行时报错找不到浏览器

执行：

```bash
playwright install chromium
```

### 已点击发布，但账号里没有看到内容

这通常说明：

- 当时只是按钮点到了，但真正发布接口没有成功返回
- 或者页面仍在处理图片

当前版本已经增加：

- 发布前等待素材稳定
- 发布接口响应检测

### 文案与主题不符

请检查输入主题是否足够明确，例如：

- 不推荐：`发一个小红书`
- 推荐：`请发一个关于TK跨境电商新手入门的小红书`

### 图片生成太慢

可以尝试：

- 复用相同主题发布，让缓存生效
- 调整 `.env` 中的 `QWEN_IMAGE_SIZE`
- 关闭 `QWEN_PROMPT_EXTEND`

## 后续可继续扩展

- 发布历史记录
- 页面里显示是否命中缓存
- 发布成功后二次校验笔记列表
- 支持定时发布
- 支持多平台发布

## License

MIT
