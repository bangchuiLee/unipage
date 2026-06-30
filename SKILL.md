---
name: diligence-pdf
description: |-
  归页 Unipage 文档汇集工具。扫描文件夹自动建立索引，智能包裹图片和 PDF（等比缩放/自动横纵/边距适配），
  生成带页码和可折叠书签的单一 PDF。支持三种模式：全自动扫描 → 索引 PDF 拆分 → 无索引直接合并。
trigger_keywords:
  - 归页
  - unipage
  - 文档汇集
  - 文件夹合并成PDF
  - 带索引的PDF
  - 扫描文件夹生成PDF
  - diligence
  - diligence-pdf
allowed-tools: Read, Write, Bash
version: 1.0.0
agent_created: true
---

# 归页 Unipage · every file finds its place

## 触发条件

用户提到"文件夹合并PDF""带索引""文档汇集""扫描文件夹"等关键词时激活。

## 交互流程

### Step 1: 理解任务文件夹

- 先扫描文件夹结构，确认目录层级、文件类型分布
- 重点关注：XLSX/XLS（需预转换）、macOS 垃圾文件（`._` / `.DS_Store` / `__MACOSX`）、EML/DOCX 等非直接支持格式
- 统计有效文件数量，预估输出页数

### Step 2: 确认参数

向用户确认以下参数，未明确指定的使用默认值：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 输入目录 | 根路径 | 必须指定 |
| 输出路径 | 最终 PDF 路径 | `输入目录/输出PDF/文档汇集.pdf` |
| 索引模式 | `auto` / `pdf` / `none` | `auto` |
| 索引来源 | 预转换的索引 PDF（仅 `pdf` 模式） | 无 |
| 图片模式 | `fit`（等比缩放）/ `split`（长图切分） | `fit` |
| 书签 | 是否添加 PDF 大纲 | 是 |
| 页码 | 是否添加页码 | 是 |

### Step 3: 执行

使用 `scripts/assembler.py` 的 `assemble()` 函数：

```python
from diligence_pdf.scripts.assembler import assemble
assemble({"input_dir": ..., "output_path": ..., ...})
```

或通过 CLI：

```bash
python -m diligence_pdf.scripts.cli assemble /path/to/dir -o output.pdf
```

运行时会显示文件统计、实时进度条和耗时。

### Step 4: 验证

- 检查边距（每页应 ≥ 18mm）
- 检查横纵方向（横向 PDF 应在横向 A4 页面上）
- 检查书签层级是否与索引一致

## 索引模式详解

### `auto` — 全自动扫描

扫描输入目录，每个子文件夹 = 一个一级索引条目。子文件夹内的子文件夹 = 二级条目。自动去 `._` 前缀和系统文件夹，生成索引标题。

### `pdf` — 预转换索引 PDF

用户已有分页索引 PDF。拆分后按顺序对应文件夹插入。要求：索引 PDF 页数 ≥ 一级文件夹数 + 二级文件夹数。

### `none` — 无索引

所有文件合并，不插入索引页。

## 文件处理策略

| 文件类型 | 策略 |
|----------|------|
| JPG/PNG/BMP/JPEG | 等比缩放适配 A4 可打印区域，居中。`split` 模式下长图切分 |
| PDF（A4 有边距） | 原样通过（零开销） |
| PDF（近A4 无边距） | `show_pdf_page` 矢量包裹加边距 |
| PDF（非标准/旋转异常） | 150dpi pixmap 光栅化渲染 |
| XLSX/XLS | **自动格式化（wrap_text + 列宽适配 + 打印缩放），在同目录生成 `_格式化.xlsx`。用户用 Excel 打开后 Ctrl+P 打印为 PDF，放回原目录即可纳入。** |
| EML/DOCX/MP4 等 | 自动跳过，输出时列出未处理文件 |

### XLSX 处理规则

- 扫描到 XLSX/XLS 时，自动调用 `scripts/xlsx_formatter.py` 格式化表格
- 处理逻辑：逐 sheet 设 wrap_text + 计算最优列宽 + 横纵判断 + fitToWidth=1 打印缩放
- 输出一份 `原文件名_格式化.xlsx` 到同目录
- 控制台打印每个 sheet 的行列数和方向，提示用户手动打印为 PDF
- 用户手动打印的 PDF 需放回原目录（与 xlsx 同名 .pdf），归页再次扫描时会自动纳入
- 如需批量导出：用项目目录下的 `format_xlsx.py --test` 测试，确认无问题后全量执行

## macOS 文件处理

自动跳过以下 macOS 系统文件：
- `._*` 资源分支文件
- `.DS_Store` 目录元数据
- `__MACOSX` 文件夹

## 环境依赖

```bash
pip install Pillow reportlab pypdf PyMuPDF openpyxl
```

## 已知问题

见 `references/known-issues.md`。
