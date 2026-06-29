<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="Apache 2.0">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
</p>

<h1 align="center">Diligence PDF</h1>
<p align="center"><strong>法律尽调底稿 — 一键汇集为打印就绪的 PDF</strong></p>

<p align="center">
  <a href="#-快速开始">快速开始</a> ·
  <a href="#-ai-agent-支持">AI Agent</a> ·
  <a href="#-安全">安全</a> ·
  <a href="#-安装">安装</a> ·
  <a href="#-许可">许可</a>
</p>

---

## 一句话

法律尽调项目中，底稿散落在十几个文件夹、几十个子目录中——营业执照、投资证书、章程、凭证扫描件，格式五花八门，方向横七竖八，打印出来缺边少页。**Diligence PDF 一口吞下整个目录，自动建索引、智能裹边距、输出一本可以直接送印的 PDF**，从此告别拼页噩梦。

---

## ✨ 功能

- **🔍 自动索引** — 扫描目录树自动生成层级索引页，无需手写 xlsx
- **📑 PDF 书签** — 自动生成可折叠大纲，1696 页也能秒级跳转
- **🖼️ 智能包裹** — 图片等比缩放不切分，PDF 三路决策树自选最佳渲染路径
- **📐 打印就绪** — 18mm 页边距 + 横纵自动适配 + 全局页码
- **⚡ 快路径优先** — 95% 页面走矢量路径，仅异常 PDF 走光栅化回退

## 📦 安装

```bash
pip install git+https://github.com/bangchuiLee/diligence-pdf.git
```

或本地克隆：

```bash
git clone https://github.com/bangchuiLee/diligence-pdf.git
cd diligence-pdf
pip install .
```

依赖：

| 包 | 版本 | 用途 |
|----|------|------|
| PyMuPDF | ≥1.24 | PDF 渲染/拆分 |
| reportlab | ≥4.0 | 索引页 + 页码生成 |
| pypdf | ≥5.0 | PDF 合并 + 书签 |
| Pillow | ≥10.0 | 图片处理 |
| openpyxl | ≥3.1 | xlsx 索引读取 |

## 🚀 快速开始

### 零配置 — 自动索引

```bash
diligence-pdf assemble /path/to/documents -o output.pdf
```

输入目录结构：

```
项目文档/
  ├── 01-公司设立/
  │   ├── 营业执照.jpg
  │   ├── 章程.pdf
  │   └── 股东名册/
  │       └── ...
  ├── 02-历次变更/
  └── ...
```

目录名自动成为索引标题，子文件夹二级索引。输出一份带书签、页码、统一边距的 PDF。

### Python API

```python
from diligence_pdf import assemble

assemble({
    "input_dir": "/path/to/documents",
    "output_path": "/path/to/output.pdf",
    "index_mode": "auto",       # auto / pdf / none
    "image_mode": "fit",        # fit（等比） / split（长图切分）
    "add_bookmarks": True,
    "add_page_numbers": True,
})
```

### 预转换索引 PDF

```python
assemble({
    "input_dir": "/path/to/documents",
    "output_path": "/path/to/output.pdf",
    "index_mode": "pdf",
    "index_source": "/path/to/index.pdf",
})
```

## 🔧 PDF 包裹决策树

```
输入 PDF 页面
  │
  ├─ A4 + 有边距 + 无旋转异常 → 原样通过（矢量、零开销）
  │
  ├─ 近 A4 + 无旋转异常 → show_pdf_page 矢量包裹（快）
  │
  └─ 非标准尺寸 或 旋转异常 → 150dpi pixmap 渲染（可靠回退）
```

## 🤖 AI Agent 支持

本工具设计为 **纯 Python 函数 + CLI**，不依赖特定框架，任何能执行 Python 代码的 AI Agent 均可直接调用。

| Agent / 平台 | 使用方式 |
|---|---|
| **Claude Code** | `pip install .` 后直接 `from diligence_pdf import assemble` |
| **Claude Desktop (MCP)** | 通过 Python 脚本 MCP Server 暴露 `assemble()` 为 tool |
| **OpenAI Codex CLI** | 支持 `pip install` + 函数调用，自动发现 API |
| **ChatGPT (Code Interpreter)** | 上传 whl 或 pip install git+URL，沙箱内直接 import |
| **Cursor / Windsurf** | 环境内 pip install 后即可在对话中调用 |
| **Aider** | 支持任意 Python 模块导入，无需额外适配 |
| **Gemini CLI** | 标准 Python 包，`pip install` 后 import 即用 |
| **GitHub Copilot Coding Agent** | 安装后自动补全建议 `assemble()` 调用 |
| **Devin** | 标准 pip 安装，可在 task 中调用 |

> **关键设计**：入口函数 `assemble(config: dict) -> str` 接受纯字典参数，无类型注解依赖、无异步操作、无状态副作用。任何 Agent 只需构造一个 dict 即可调用。

## 🔒 安全

### 零网络承诺

本工具**完全本地运行**。不会、也不需要发起任何网络请求：

- ❌ 无 API 调用
- ❌ 无遥测 / 埋点
- ❌ 无数据上传
- ❌ 无凭据存储
- ❌ 无第三方服务依赖

你可以断网运行，抓包验证，审计源码——总共 1200 行 Python，无混淆、无动态执行。

### 依赖审计

| 依赖 | 许可证 | 下载量 |
|------|--------|--------|
| PyMuPDF | AGPL | 50M+ |
| reportlab | BSD | 30M+ |
| pypdf | BSD | 80M+ |
| Pillow | HPND-C | 500M+ |
| openpyxl | MIT | 200M+ |

所有依赖均为 PyPI 官方包，许可证均允许本地使用。

> ⚠️ **注意**：PyMuPDF 使用 AGPL v3。本地 CLI / AI Agent 调用不触发 copyleft 条款。如需商用 SaaS 部署（网络分发），请替换为纯 pypdf 方案或咨询法律顾问。

## ⚙️ 完整配置

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_dir` | Path | 必填 | 底稿根目录 |
| `output_path` | Path | 必填 | 输出 PDF 路径 |
| `index_mode` | str | `auto` | `auto` / `pdf` / `none` |
| `index_source` | Path | — | 索引 PDF（`pdf` 模式） |
| `image_mode` | str | `fit` | `fit`（等比缩放）/ `split`（长图切分） |
| `add_bookmarks` | bool | `true` | PDF 书签 |
| `add_page_numbers` | bool | `true` | 页码 |
| `include_tables` | bool | `false` | 尝试处理 xls/xlsx |

## 📄 许可

Apache License 2.0 — 详见 [LICENSE](./LICENSE)

---

<p align="center"><sub>Built for legal professionals who want their documents in order, not in pieces.</sub></p>
