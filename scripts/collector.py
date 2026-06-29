#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件收集与过滤
"""

from .constants import IMAGE_EXTS, TABLE_EXTS, SKIP_NAMES, SKIP_PREFIX


def should_skip(name):
    """是否应跳过（macOS 资源分叉 + Windows 缩略图 + 系统文件）"""
    return name.startswith(SKIP_PREFIX) or name in SKIP_NAMES


def is_supported(filepath, include_tables=False):
    """判断文件是否支持处理"""
    ext = filepath.suffix.lower()
    if include_tables:
        return ext in IMAGE_EXTS or ext == '.pdf' or ext in TABLE_EXTS
    return ext in IMAGE_EXTS or ext == '.pdf'


def collect_folder(folder, include_tables=False):
    """收集文件夹：根级文件按名 → 子文件夹按名递归"""
    if not folder.is_dir():
        return []
    root = sorted(
        [f for f in folder.iterdir()
         if f.is_file() and is_supported(f, include_tables)
         and not should_skip(f.name)],
        key=lambda x: x.name
    )
    subs = sorted(
        [d for d in folder.iterdir()
         if d.is_dir() and not should_skip(d.name)],
        key=lambda d: d.name
    )
    result = list(root)
    for s in subs:
        result.extend(collect_folder(s, include_tables))
    return result


def resolve_item(parent, row_text):
    """在父目录下模糊匹配文件名/文件夹名"""
    txt = row_text.strip()
    exact = parent / txt
    if exact.exists():
        return exact
    for ext in ['.pdf', '.docx', '.doc', '.jpg', '.jpeg',
                 '.png', '.bmp', '.PDF', '.DOCX']:
        candidate = parent / (txt + ext)
        if candidate.exists():
            return candidate
    if parent.is_dir():
        for child in sorted(parent.iterdir()):
            if should_skip(child.name):
                continue
            stem = child.stem
            if stem == txt or stem.startswith(txt) or txt in child.name:
                return child
    return None
