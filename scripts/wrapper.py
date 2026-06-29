#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 智能包裹 — 三路决策树
"""

import io
import fitz
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader

from .constants import (
    A4_W, A4_H, PRINT_W_P, PRINT_H_P, PRINT_W_L, PRINT_H_L
)


def get_content_bbox(page):
    """计算页面内容包围盒（图片 + 文字 + 矢量图形并集）"""
    bbox = None
    for img in page.get_image_info():
        r = fitz.Rect(img['bbox'])
        bbox = r if bbox is None else bbox | r
    for block in page.get_text("blocks"):
        if block[6] == 0:
            r = fitz.Rect(block[0], block[1], block[2], block[3])
            bbox = r if bbox is None else bbox | r
    for d in page.get_drawings():
        bbox = d['rect'] if bbox is None else bbox | d['rect']
    return bbox or page.rect


def _wrap_via_show(src_doc, page_num, pw, ph):
    """show_pdf_page 矢量包裹 — 适用于接近 A4 的页面"""
    is_landscape = pw > ph
    canvas_w, canvas_h = (A4_H, A4_W) if is_landscape else (A4_W, A4_H)
    print_w, print_h = (PRINT_W_L, PRINT_H_L) if is_landscape else (PRINT_W_P, PRINT_H_P)
    scale = min(print_w / pw, print_h / ph)
    sw = pw * scale
    sh = ph * scale
    x = (canvas_w - sw) / 2
    y = (canvas_h - sh) / 2
    target = fitz.Rect(x, y, x + sw, y + sh)
    new_doc = fitz.open()
    new_page = new_doc.new_page(width=canvas_w, height=canvas_h)
    new_page.show_pdf_page(target, src_doc, page_num)
    buf = io.BytesIO()
    new_doc.save(buf)
    new_doc.close()
    buf.seek(0)
    return buf


def _wrap_via_pixmap(src_doc, page_num, pw, ph, dpi=150):
    """pixmap 渲染包裹 — 适用于非标准尺寸或有旋转异常的 PDF"""
    is_landscape = pw > ph
    canvas_w, canvas_h = (A4_H, A4_W) if is_landscape else (A4_W, A4_H)
    print_w, print_h = (PRINT_W_L, PRINT_H_L) if is_landscape else (PRINT_W_P, PRINT_H_P)
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    pix = src_doc[page_num].get_pixmap(matrix=mat)
    pix_w_pt = pix.width * 72 / dpi
    pix_h_pt = pix.height * 72 / dpi
    scale = min(print_w / pix_w_pt, print_h / pix_h_pt)
    draw_w = pix_w_pt * scale
    draw_h = pix_h_pt * scale
    x = (canvas_w - draw_w) / 2
    y = (canvas_h - draw_h) / 2
    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=(canvas_w, canvas_h))
    c.setPageCompression(1)
    c.drawImage(ImageReader(io.BytesIO(pix.tobytes("png"))), x, y,
                width=draw_w, height=draw_h)
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def wrap_pdf_page(src_doc, page_num):
    """
    智能包裹已有 PDF 页面，三路决策：
    1. A4 + 有边距 + 无越界 → 原样通过（矢量，零开销）
    2. 近A4 + 无越界 → show_pdf_page 包裹（矢量，快）
    3. 非标准尺寸或内容越界 → pixmap 渲染（位图，可靠）
    """
    page = src_doc[page_num]
    pw, ph = page.rect.width, page.rect.height

    bbox_raw = get_content_bbox(page)
    bbox_overflow = (bbox_raw.width > pw + 2 or bbox_raw.height > ph + 2)
    bbox = bbox_raw & page.rect
    min_m = min(bbox.y0, ph - bbox.y1, bbox.x0, pw - bbox.x1)

    is_a4_p = abs(pw - A4_W) < 2 and abs(ph - A4_H) < 2
    is_a4_l = abs(pw - A4_H) < 2 and abs(ph - A4_W) < 2
    near_a4 = is_a4_p or is_a4_l

    # 情况1: 已有边距 + A4 + 无越界
    if min_m >= 10 and near_a4 and not bbox_overflow:
        buf = io.BytesIO()
        tmp_doc = fitz.open()
        tmp_doc.insert_pdf(src_doc, from_page=page_num, to_page=page_num)
        tmp_doc.save(buf)
        tmp_doc.close()
        buf.seek(0)
        return buf

    # 情况2: 接近 A4 + 无越界
    if near_a4 and not bbox_overflow:
        return _wrap_via_show(src_doc, page_num, pw, ph)

    # 情况3: 非标准或越界
    return _wrap_via_pixmap(src_doc, page_num, pw, ph)
