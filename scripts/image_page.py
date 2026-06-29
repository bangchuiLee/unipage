#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图片处理 — 等比缩放 / 长图切分
"""

import io
from PIL import Image
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.lib.utils import ImageReader

from .constants import (
    A4_W, A4_H, MARGIN, PRINT_W_P, PRINT_H_P, PRINT_W_L, PRINT_H_L
)


def image_to_page(img_path):
    """单张图片等比缩放适配一页 A4，不做切分"""
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    is_landscape = w > h

    if is_landscape:
        pw, ph = A4_H, A4_W
        print_w, print_h = PRINT_W_L, PRINT_H_L
    else:
        pw, ph = A4_W, A4_H
        print_w, print_h = PRINT_W_P, PRINT_H_P

    scale = min(print_w / w, print_h / h)
    sw = w * scale
    sh = h * scale
    x = (pw - sw) / 2
    y = (ph - sh) / 2

    buf = io.BytesIO()
    c = rl_canvas.Canvas(buf, pagesize=(pw, ph))
    c.setPageCompression(1)
    c.drawImage(ImageReader(img), x, y, width=sw, height=sh,
                preserveAspectRatio=True, anchor='nw')
    c.showPage()
    c.save()
    buf.seek(0)
    return buf


def split_image_pages(img_path):
    """长图自动纵向分页 — 返回 [(chunk_img, is_landscape), ...]"""
    img = Image.open(img_path).convert('RGB')
    w, h = img.size
    is_landscape = w > h

    print_w = PRINT_W_L if is_landscape else PRINT_W_P
    print_h = PRINT_H_L if is_landscape else PRINT_H_P
    scale = print_w / w
    scaled_h = h * scale

    chunks = []
    if scaled_h <= print_h:
        chunks.append((img.copy(), is_landscape))
    else:
        crop_px = int(print_h / scale)
        n_pages = (h + crop_px - 1) // crop_px
        for i in range(n_pages):
            top = i * crop_px
            bot = min((i + 1) * crop_px, h)
            chunks.append((img.crop((0, top, w, bot)), is_landscape))
    return chunks


def chunk_to_page(chunk_img, is_landscape):
    """图片切片转为单页 PDF"""
    buf = io.BytesIO()
    pw = A4_H if is_landscape else A4_W
    ph = A4_W if is_landscape else A4_H
    c = rl_canvas.Canvas(buf, pagesize=(pw, ph))
    c.setPageCompression(1)
    cw, ch = chunk_img.size
    pw_print = PRINT_W_L if is_landscape else PRINT_W_P
    scale = pw_print / cw
    dh = ch * scale
    x = MARGIN
    y = ph - MARGIN - dh
    c.drawImage(ImageReader(chunk_img), x, y, width=pw_print, height=dh,
                preserveAspectRatio=True, anchor='nw')
    c.showPage()
    c.save()
    buf.seek(0)
    return buf
