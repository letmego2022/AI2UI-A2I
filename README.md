# 🤖 A2I: AI-Powered Visual UI Automation

[English](./README.en.md) | **简体中文**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Stars](https://img.shields.io/github/stars/letmego2022/AI2UI-A2I?style=social)](https://github.com/letmego2022/AI2UI-A2I/stargazers)
[![Issues](https://img.shields.io/github/issues/letmego2022/AI2UI-A2I)](https://github.com/letmego2022/AI2UI-A2I/issues)

**A2I 是一个基于视觉理解的 UI 自动化平台，它将大语言模型 (LLM) 的推理能力与稳健的浏览器自动化技术相结合，让你能通过自然语言指令完成复杂的网页操作与自动化测试。**

---

## 🎥 动态演示 (Live Demo)

眼见为实！点击下方查看 A2I 的实时操作演示，了解它如何将自然语言转化为精确的 UI 操作。

[![A2I Demo Video](https://github.com/user-attachments/assets/e7c3e29b-4b64-42d3-a1fa-8a0e724619e0)](https://www.bilibili.com/video/BV1zD8MzLEFB/)
*<p align="center">点击图片观看演示视频</p>*

---

## ✨ 核心特性 (Features)

-   🧠 **智能指令解析 (Intelligent Instruction Parsing)**：基于 LLM 理解模糊的自然语言任务描述（如“帮我登录”、“搜索最新的 AI 新闻”），并自动推理出具体的操作步骤序列。
-   👁️ **精准视觉定位 (Precise Visual Grounding)**：不依赖脆弱的 XPath/CSS 选择器，通过视觉模型在截图上直接定位操作元素（按钮、输入框等），极大提升了对动态页面的适应性。
-   📸 **可视化操作追溯 (Visualized Action Traceability)**：每一步操作都会自动截图，并高亮标记当前操作的元素和区域。整个流程清晰可见，便于调试和验证。
-   🧩 **模块化与可扩展 (Modular & Extensible)**：核心引擎、AI 模型和执行器均采用模块化设计，方便替换或扩展，你可以轻松接入不同的 LLM（GPT-4o, Claude 3, Moonshot 等）。
-   💬 **交互式对话界面 (Interactive Chat Interface)**：提供简洁直观的 GUI，像聊天一样输入你的任务，即刻获得自动化执行结果。

---

## 🔧 工作原理 (How It Works)

A2I 的工作流程非常直观：

1.  **输入 (Input)**: 用户在前端界面输入一个高级指令（例如：“搜索 A2I 项目并进入它的 GitHub 页面”）。
2.  **感知 (Perceive)**: 系统自动对当前浏览器页面进行截图。
3.  **思考 (Think)**: 将用户指令和页面截图一同发送给大语言模型 (LLM)。
4.  **规划 (Plan)**: LLM 分析视觉信息和指令，生成一个具体的操作指令（例如：`{ "action": "type", "text": "A2I github", "element_description": "搜索框" }`）。
5.  **执行 (Act)**: 执行器（Playwright）根据指令在浏览器上执行相应的操作（如点击、输入、滚动）。
6.  **循环 (Loop)**: 重复 2-5 步，直到完成用户指定的最终任务。

---

## 🛠️ 技术栈 (Tech Stack)

-   **前端 (Frontend)**: `Flask` + `Bootstrap 5` + `Jinja2`
-   **后端 (Backend)**: `Python 3.9+`
-   **浏览器自动化 (Browser Automation)**: `Playwright`
-   **AI 大语言模型 (LLMs)**: 可插拔架构，默认支持 `GPT-4` / `Moonshot` / `Claude` 系列及其他兼容 OpenAI API 的模型。

---

## 🚀 快速开始 (Getting Started)

### 1. 环境准备

-   确保你已安装 `Python 3.9+` 和 `Git`。

### 2. 安装与配置

```bash
# 1. 克隆项目
git clone https://github.com/your-name/uioperator.git
cd uioperator

# 2. 创建并激活虚拟环境 (推荐)
python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`

# 3. 安装依赖
pip install -r requirements.txt

# 4. 安装 Playwright 浏览器驱动
playwright install

# 5. 配置环境变量
# 复制 .env.example 文件为 .env，并填入你的 API Key
cp .env.example .env
# 编辑 .env 文件
# nano .env
```
**`.env` 文件内容示例:**
```env
# OPENAI_API_KEY="sk-..."
MOONSHOT_API_KEY="your-moonshot-api-key"
```

### 3. 启动服务

```bash
# 启动 Flask 应用
python app.py
```
现在，在浏览器中打开 `http://127.0.0.1:5000` 即可开始使用！

---

## 🛣️ 路线图 (Roadmap)

-   [x] GUI 可交互式任务输入框
-   [x] 截图+坐标标注系统
-   [x] AI 指令生成器（点击 / 输入 / 拖动）
-   [x] 多步执行追踪 + 缩略图展示
-   [ ] 📁 **流程录制与回放**: 记录用户操作序列并一键重放。
-   [ ] 🔄 **任务编辑与重执行**: 支持在多步流程中修改某一步并从该点继续执行。
-   [ ] 🧩 **插件化架构**: 引入插件系统以支持自定义操作（如 API 调用、数据检查）。
-   [ ] 🌐 **Docker 一键部署**: 提供 Dockerfile，实现隔离环境的快速部署。

---

## 🤝 参与贡献 (Contributing)

我们热烈欢迎各种形式的贡献！无论是提交 Issue、改进文档，还是贡献代码。

请遵循标准的 **Fork & Pull Request** 流程：
1.  **Fork** 本项目到你的仓库。
2.  从 `main` 分支创建一个新的特性分支 (`git checkout -b feature/your-amazing-feature`)。
3.  进行修改并提交 (`git commit -m 'feat: Add some amazing feature'`)。
4.  将你的分支推送到你的 Fork 仓库 (`git push origin feature/your-amazing-feature`)。
5.  创建一个 **Pull Request** 请求合并到本项目的 `main` 分支。

如果你有任何建议或问题，请随时在 [Issue 区](https://github.com/letmego2022/AI2UI-A2I/issues)提出！

---

## 📄 许可证 (License)

本项目基于 [MIT License](LICENSE) 开源。
```
