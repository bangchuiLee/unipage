<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/license-MIT-green.svg" alt="MIT License">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
  <img src="https://img.shields.io/badge/PDF%20quality-print%20ready-important.svg" alt="Print Ready">
</p>

<h1 align="center">Diligence PDF</h1>
<p align="center"><strong>尽调底稿 PDF 汇集工具</strong></p>

<p align="center">扫描文件夹自动建立索引 · 智能包裹图片和PDF · 生成带书签和页码的单一PDF</p>

---

## ✨ 功能

- **🔍 自动索引** — 扫描目录结构，自动生成层级索引页，无需手写 xlsx
- **📑 PDF 书签** — 自动生成可折叠大纲，1696 页也能秒级跳转
- **🖼️ 智能包裹** — 图片等比缩放不切分，PDF 三路决策树自动选择最佳渲染路径
- **📐 打印就绪** — 18mm 页边距 + 横纵自动适配 + 全局页码
- **⚡ 快路径优先** — 95% 页面走矢量路径，仅异常 PDF 走光栅化回退
- **🛡️ 零网络** — 纯本地运行，不调 API、不上传数据

## 📦 安装

```bash
pip install git+https://github.com/your/diligence-pdf.git
```

依赖会自动安装：

| 包 | 用途 |
|----|------|
| PyMuPDF | PDF 渲染/拆分 |
| reportlab | PDF 生成（索引页 + 页码） |
| pypdf | PDF 合并 + 书签 |
| Pillow | 图片处理 |
| openpyxl | xlsx 索引读取（可选） |

## 🚀 快速开始

### 零配置模式

```bash
python -m diligence_pdf.scripts.assembler /path/to/documents -o output.pdf
```

输入目录结构：

```
项目文档/
  ├── 第一章-公司设立/
  │   ├── 营业执照.jpg
  │   ├── 章程.pdf
  │   └── 股东名册/
  │       └── ...
  ├── 第二章-公司变更/
  └── ...
```

工具自动将 `第一章-公司设立`、`第二章-公司变更` 作为一级索引，子文件夹作为二级索引。

### 使用预转换索引 PDF

```python
from scripts.assembler import assemble

assemble({
    "input_dir": "/path/to/documents",
    "output_path": "/path/to/output.pdf",
    "index_mode": "pdf",
    "index_source": "/path/to/index.pdf",
    "image_mode": "fit",
    "add_bookmarks": True,
})
```

### 直接合并（无索引）

```python
assemble({
    "input_dir": "/path/to/documents",
    "index_mode": "none",
})
```

## ⚙️ 配置参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_dir` | Path | 必填 | 底稿根目录 |
| `output_path` | Path | 必填 | 输出 PDF 路径 |
| `index_mode` | str | `auto` | `auto` / `pdf` / `none` |
| `index_source` | Path | — | 预转换索引 PDF（`pdf` 模式） |
| `image_mode` | str | `fit` | `fit`（等比缩放）/ `split`（长图切分） |
| `add_bookmarks` | bool | `true` | 是否添加 PDF 书签 |
| `add_page_numbers` | bool | `true` | 是否添加页码 |
| `include_tables` | bool | `false` | 是否尝试处理 xls/xlsx（需预转 PDF） |

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

## 🧪 已验证场景

- ✅ 横版 / 纵版 PDF 自动适配
- ✅ 旋转图像异常 PDF（投资证书类）自动光栅化
- ✅ macOS 资源分叉（`._`）自动过滤
- ✅ 长图自动切分 / 等比缩放双模式
- ✅ 500+ 文件、1500+ 页大规模项目
- ✅ WorkBuddy sandbox 兼容

## 🤝 WorkBuddy Skill

本项目同时是 [WorkBuddy](https://codebuddy.cn) 的官方 Skill，安装后可直接对话式使用：

> "帮我把这个目录的尽调底稿合并成带索引的 PDF"

详见 [SKILL.md](./SKILL.md)

## 📄 许可

MIT License — 详见 [LICENSE](./LICENSE)

---

<p align="center"><sub>Built with ❤️ for legal professionals who just want their documents in order.</sub></p>
