#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常量与字体检测
"""

import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# --- 页面尺寸 ---
A4_W, A4_H = A4
MARGIN = 18 * mm
PRINT_W_P = A4_W - 2 * MARGIN
PRINT_H_P = A4_H - 2 * MARGIN
PRINT_W_L = A4_H - 2 * MARGIN
PRINT_H_L = A4_W - 2 * MARGIN

# --- 文件类型 ---
IMAGE_EXTS = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.PNG', '.JPG', '.JPEG'}
TABLE_EXTS = {'.xls', '.xlsx', '.xlsm'}

# --- 文件过滤 ---
SKIP_NAMES = {'Thumbs.db', '.DS_Store', 'desktop.ini'}
SKIP_PREFIX = '._'

# --- 字体 ---
FONT_NAME = "CJK"
FONT_PATH = None
_FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyh.ttc",
    "C:/Windows/Fonts/simsun.ttc",
    "C:/Windows/Fonts/simhei.ttf",
]

for _fp in _FONT_CANDIDATES:
    if os.path.exists(_fp):
        try:
            pdfmetrics.registerFont(TTFont(FONT_NAME, _fp))
            FONT_PATH = _fp
            break
        except Exception:
            pass

if not FONT_PATH:
    FONT_NAME = "Helvetica"


def ensure_font():
    """确保字体已注册（幂等调用）"""
    return FONT_NAME
