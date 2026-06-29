---
name: diligence-pdf
description: |-
  尽调底稿 PDF 汇集工具。扫描文件夹自动建立索引，智能包裹图片和 PDF（等比缩放/自动横纵/边距适配），
  生成带页码和可折叠书签的单一 PDF。支持三种模式：全自动扫描 → 索引 PDF 拆分 → 无索引直接合并。
trigger_keywords:
  - 尽调底稿
  - PDF汇集
  - 底稿合并
  - 文件夹合并成PDF
  - 带索引的PDF
  - diligence
  - diligence-pdf
allowed-tools: Read, Write, Bash
version: 1.0.0
agent_created: true
---

# 尽调底稿 PDF 汇集

## 触发条件

用户提到"尽调底稿""合并成PDF""带索引""扫描文件夹生成PDF"等关键词时激活。

## 交互流程

### Step 1: 收集信息

向用户确认以下参数，未明确指定的使用默认值：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 输入目录 | 底稿文件夹根路径 | 必须指定 |
| 输出路径 | 最终 PDF 路径 | `输入目录/输出PDF/底稿汇集.pdf` |
| 索引模式 | `auto` / `pdf` / `none` | `auto` |
| 索引来源 | 预转换的索引 PDF（仅 `pdf` 模式） | 无 |
| 图片模式 | `fit`（等比缩放）/ `split`（长图切分） | `fit` |
| 书签 | 是否添加 PDF 大纲 | 是 |
| 页码 | 是否添加页码 | 是 |

### Step 2: 执行

使用 `scripts/assembler.py` 的 `assemble()` 函数：

```python
from diligence_pdf.scripts.assembler import assemble
assemble({"input_dir": ..., "output_path": ..., ...})
```

或通过 CLI：

```bash
python -m diligence_pdf.scripts.cli assemble /path/to/dir -o output.pdf
```

### Step 3: 验证

- 检查边距（每页应 ≥ 18mm）
- 检查横纵方向（横向 PDF 应在横向 A4 页面上）
- 检查书签层级是否与索引一致
- 打印总数对比（实际文件数 vs 报告文件数）

## 索引模式详解

### `auto` — 全自动扫描

扫描输入目录，每个子文件夹 = 一个一级索引条目。子文件夹内的子文件夹 = 二级条目。自动去 `.` 前缀和扩展名生成索引标题。

### `pdf` — 预转换索引 PDF

用户已有分页索引 PDF。拆分后按顺序对应文件夹插入。要求：索引 PDF 页数 ≥ 一级文件夹数 + 二级文件夹数。

### `none` — 无索引

所有文件合并，不插入索引页。

## 文件处理策略

| 文件类型 | 策略 |
|----------|------|
| JPG/PNG/BMP | 等比缩放适配 A4 可打印区域，居中。`split` 模式下长图切分 |
| PDF（A4 有边距） | 原样通过（零开销） |
| PDF（近A4 无边距） | `show_pdf_page` 矢量包裹加边距 |
| PDF（非标准/旋转异常） | 150dpi pixmap 光栅化渲染 |
| XLS/XLSX | 需用户预转换为 PDF 后提供路径 |

## 环境依赖

```bash
pip install Pillow reportlab pypdf PyMuPDF openpyxl
```

## 已知问题

见 `references/known-issues.md`。
