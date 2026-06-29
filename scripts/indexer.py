#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
索引生成 — 拆分预转 PDF + 动态生成 + 自动扫描目录
"""

import io
import os
import fitz
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.pagesizes import A4

from .constants import FONT_NAME


def split_index_pdf(index_pdf_path, out_dir):
    """将索引 PDF 拆为单页 → out_dir/index_01.pdf ~ index_NN.pdf"""
    doc = fitz.open(str(index_pdf_path))
    n = doc.page_count
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for i in range(n):
        new_doc = fitz.open()
        new_doc.insert_pdf(doc, from_page=i, to_page=i)
        out_path = os.path.join(out_dir, f"index_{i+1:02d}.pdf")
        new_doc.save(out_path)
        new_doc.close()
        paths.append(out_path)
    doc.close()
    return paths


def make_index_page(title, font_size=16, alignment='left'):
    """动态生成索引用 A4 页面（左对齐、垂直居中）"""
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=A4)
    cw, ch = A4
    c.setFont(FONT_NAME, font_size)

    if alignment == 'left':
        left_margin = 1797 / 72  # ≈25mm (参考标准 docx 左边距 DXA→pt)
        c.drawString(left_margin, ch / 2, title)
    else:
        c.drawCentredString(cw / 2, ch / 2, title)

    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def auto_index_from_folders(root_dir):
    """
    自动扫描目录结构生成索引树。
    每个一级子文件夹 = 一个索引条目。
    如果一级子文件夹有子文件夹 = 二级索引条目。
    返回: [{page_num, title, path, children}, ...]
    """
    from pathlib import Path as _Path
    root = root_dir if hasattr(root_dir, 'iterdir') else _Path(root_dir)
    if not root.is_dir():
        return []

    tree = []
    page = 0
    items = sorted([d for d in root.iterdir() if d.is_dir()], key=lambda x: x.name)

    for item in items:
        page += 1
        entry = {
            "page_num": page,
            "title": item.name,
            "path": item,
            "children": [],
        }
        subdirs = sorted([d for d in item.iterdir() if d.is_dir()], key=lambda x: x.name)
        for sub in subdirs:
            page += 1
            entry["children"].append({
                "page_num": page,
                "title": sub.name,
                "path": sub,
            })
        tree.append(entry)

    return tree
