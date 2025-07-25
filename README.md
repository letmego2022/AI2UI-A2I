# 🤖 A2I：基于 AI 的视觉 UI 自动化平台

A2I 是一个基于视觉理解的 UI 自动化平台，结合 AI 能力与自动化执行技术，实现通过自然语言控制网页操作，特别适用于复杂页面的快速交互和自动化测试。

---

## ✨ 项目亮点

- 🧠 **AI 驱动任务理解**：通过自然语言任务描述，自动推理出 UI 操作序列
- 🖱️ **视觉识别+操作执行**：基于 Playwright 结合视觉标注技术精准执行
- 🖼️ **截图 + 标注 + 回放**：每一步自动截图，高亮操作区域，支持可视化追踪
- 📦 **模块化结构**：支持插件式识别引擎、操作生成器与执行器
- 🔎 **对话式界面**：提供简洁直观的 GUI 输入框，可交互式输入任务描述

---

## 📷 实时界面预览

| 任务输入 | 多步执行流程追踪 | 视觉标注截图 |
|----------|------------------|---------------|
| <img width="1453" height="571" alt="image" src="https://github.com/user-attachments/assets/e7c3e29b-4b64-42d3-a1fa-8a0e724619e0" />
 | <img width="1252" height="600" alt="image" src="https://github.com/user-attachments/assets/07508f19-c1d3-4e5c-a782-c2504d2bb464" />
 | <img width="1269" height="764" alt="image" src="https://github.com/user-attachments/assets/7430f381-7aae-48e0-93a3-8f3e21e3e38f" />
 |

---

## 🔧 当前技术架构

- 前端：`Flask + Bootstrap5` 简洁 UI
- 后端：`Python` 处理任务分发与截图处理
- 执行引擎：`Playwright` 自动浏览器操作
- 智能引擎：支持任意可替换的 LLM，例如 `GPT-4` / `Moonshot` / `Claude`

---

## 🛣️ 开发路线图（Roadmap）

- [x] GUI 可交互式任务输入框
- [x] 截图+坐标标注系统
- [x] AI 指令生成器（点击 / 输入 / 拖动）
- [x] 多步执行追踪 + 缩略图展示
- [ ] 📁 流程录制与回放功能
- [ ] 🔄 支持任务编辑与重执行
- [ ] 🧩 插件机制支持更多操作类型
- [ ] 🌐 Docker 一键部署

---

## 🤝 贡献指南

欢迎贡献者一同完善本项目：

```bash
# 克隆项目
git clone https://github.com/your-name/uioperator.git
cd uioperator

# 安装依赖
pip install -r requirements.txt

# 启动服务
python app.py
````

如有建议、PR 或 Feature Request，请前往 [Issue 区](https://github.com/your-name/uioperator/issues)！

---

## ⚡ 灵感来源

本项目灵感来自 AI + UI 自动化结合场景，致力于推动“零代码自动操作”在实际工程中的落地应用。

---

## 📄 License

[MIT License](LICENSE)


