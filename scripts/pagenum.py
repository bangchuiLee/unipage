#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
页码叠加 — 每页底部居中 "第x页，共N页"
"""

import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas as rl_canvas

from .constants import FONT_NAME


def add_page_numbers(input_pdf, output_pdf=None, font_size=9):
    """读入 PDF，每页底部居中叠加页码，返回总页数"""
    reader = PdfReader(input_pdf)
    writer = PdfWriter()
    total = len(reader.pages)

    for i, page in enumerate(reader.pages):
        pw = float(page.mediabox.width)
        ph = float(page.mediabox.height)

        overlay_buf = io.BytesIO()
        c = rl_canvas.Canvas(overlay_buf, pagesize=(pw, ph))
        c.setFont(FONT_NAME, font_size)
        c.drawCentredString(pw / 2, 20, f"第{i + 1}页，共{total}页")
        c.save()
        overlay_buf.seek(0)

        overlay = PdfReader(overlay_buf)
        page.merge_page(overlay.pages[0])
        writer.add_page(page)

    out = output_pdf or input_pdf
    with open(out, 'wb') as f:
        writer.write(f)
    return total
