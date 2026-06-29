#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 书签（大纲）生成
"""

from pypdf import PdfReader, PdfWriter


class Bookmark:
    """书签节点"""
    def __init__(self, title, page, level=0):
        self.title = title
        self.page = page
        self.level = level
        self.children = []


def add_bookmarks(pdf_path, bookmarks, output_path=None):
    """
    写入 PDF 大纲。
    bookmarks: list[Bookmark]，支持嵌套 children。
    """
    reader = PdfReader(pdf_path)
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    _add_bookmark_tree(writer, None, bookmarks)

    out = output_path or pdf_path
    with open(out, 'wb') as f:
        writer.write(f)
    return out


def _add_bookmark_tree(writer, parent_ref, bookmarks):
    for bm in bookmarks:
        ref = writer.add_outline_item(bm.title, bm.page - 1, parent=parent_ref)
        if bm.children:
            _add_bookmark_tree(writer, ref, bm.children)


def collect_bookmarks_from_index_tree(index_tree, page_map):
    """
    从索引树和页码映射生成 Bookmark 列表。
    index_tree: [{page_num, title, children}, ...]
    page_map: {index_page_num: output_page_number}
    """
    result = []
    for entry in index_tree:
        bm = Bookmark(
            title=entry["title"],
            page=page_map.get(entry["page_num"], 1),
            level=0
        )
        for child in entry.get("children", []):
            bm.children.append(Bookmark(
                title=child["title"],
                page=page_map.get(child["page_num"], 1),
                level=1
            ))
        result.append(bm)
    return result
