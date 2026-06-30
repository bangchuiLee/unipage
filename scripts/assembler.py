#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主流水线 — 组装索引树 + 文件处理 + 合并 + 页码 + 书签
"""

import io
import os
import sys
import time
import tempfile
from pathlib import Path

# 确保 skill 目录在 sys.path 上
_SKILL_DIR = Path(__file__).resolve().parent.parent
if str(_SKILL_DIR) not in sys.path:
    sys.path.insert(0, str(_SKILL_DIR))

import fitz
from pypdf import PdfReader, PdfWriter

from scripts.constants import IMAGE_EXTS, TABLE_EXTS
from scripts.wrapper import wrap_pdf_page
from scripts.image_page import image_to_page, split_image_pages, chunk_to_page
from scripts.collector import should_skip, is_supported, collect_folder, resolve_item
from scripts.indexer import split_index_pdf, make_index_page, auto_index_from_folders
from scripts.bookmarks import collect_bookmarks_from_index_tree, add_bookmarks
from scripts.pagenum import add_page_numbers
from scripts.xlsx_formatter import format_xlsx


def _process_file(filepath, writer, image_mode='fit', progress=None):
    """处理单个文件加入 PdfWriter"""
    fname = filepath.name
    ext = filepath.suffix.lower()

    if ext in IMAGE_EXTS:
        try:
            if image_mode == 'split':
                chunks = split_image_pages(str(filepath))
                for chunk_img, is_landscape in chunks:
                    buf = chunk_to_page(chunk_img, is_landscape)
                    writer.add_page(PdfReader(buf).pages[0])
            else:
                buf = image_to_page(str(filepath))
                writer.add_page(PdfReader(buf).pages[0])
        except Exception as e:
            print(f"\n  [SKIP] {fname}: {e}")

    elif ext == '.pdf':
        try:
            src = fitz.open(str(filepath))
        except Exception as e:
            print(f"\n  [SKIP] {fname}: {e}")
            return
        for pn in range(src.page_count):
            try:
                buf = wrap_pdf_page(src, pn)
                r = PdfReader(buf)
                for pg in r.pages:
                    writer.add_page(pg)
            except Exception as e:
                print(f"\n  [SKIP] {fname} p{pn+1}: {e}")
        src.close()

    elif ext in TABLE_EXTS:
        # 如果同目录已有同名 PDF，说明用户已手动转换，跳过
        pdf_sibling = filepath.with_suffix('.pdf')
        if pdf_sibling.exists():
            pass  # 已有 PDF，静默跳过
        else:
            try:
                result = format_xlsx(str(filepath))
                formatted = result["path"]
                sheets_info = ", ".join(
                    f"{s['name']}({s['rows']}行×{s['cols']}列,{s['orientation']})"
                    for s in result["sheets"]
                )
                print(f"\n  [XLSX] {fname} 已格式化 → {Path(formatted).name}")
                print(f"         请用 Excel 打开 → Ctrl+P 打印为 PDF，放回原目录")
                print(f"         共 {len(result['sheets'])} 个 sheet: {sheets_info}")
            except Exception as e:
                print(f"\n  [XLSX] {fname}: 格式化失败 ({e})，请手动转换为 PDF")

    if progress is not None:
        progress['done'] += 1
        done = progress['done']
        total = progress['total']
        pct = done * 100 // total if total > 0 else 100
        bar = '#' * (pct // 5) + '.' * (20 - pct // 5)
        print(f"\r  [{bar}] {pct}% ({done}/{total})", end='', flush=True)


def _process_node(node, writer, index_paths, page_map, config, progress=None):
    """处理索引树节点（递归）"""
    image_mode = config.get('image_mode', 'fit')
    page_map[node['page_num']] = len(writer.pages) + 1

    # 索引页
    if node.get('index_pdf_path'):
        r = PdfReader(node['index_pdf_path'])
        writer.add_page(r.pages[0])
    elif node.get('gen_index'):
        buf = make_index_page(node['title'], node.get('font_size', 16), node.get('alignment', 'left'))
        writer.add_page(PdfReader(buf).pages[0])

    # 内容
    node_type = node.get('type', 'folder')
    if node_type == 'folder':
        files = collect_folder(node['path'], config.get('include_tables', False))
        for f in files:
            _process_file(f, writer, image_mode, progress)

    elif node_type == 'file':
        if node['path'].exists():
            _process_file(node['path'], writer, image_mode, progress)

    elif node_type == 'index_only':
        pass  # 只放索引页，无内容

    # 子节点
    for child in node.get('children', []):
        _process_node(child, writer, index_paths, page_map, config, progress)


def assemble(config):
    """
    主入口。
    config 必需: input_dir, output_path
    config 可选: index_mode, index_source, image_mode, margin,
                 add_bookmarks, add_page_numbers, include_tables
    """
    input_dir = Path(config['input_dir'])
    output_path = Path(config['output_path'])
    t_start = time.time()

    print("+" + "-" * 50 + "+")
    print(f"|  Unipage v1.0{' ' * 35}|")
    print("|" + " " * 50 + "|")
    print(f"|  [dir] 输入目录   {str(input_dir)[:37]:<37} |")

    # Phase 1: 构建索引树
    index_mode = config.get('index_mode', 'auto')
    index_source = config.get('index_source')

    if index_mode == 'auto':
        print("|  [scan] 索引模式   自动扫描目录生成索引                  |")
        index_tree = auto_index_from_folders(input_dir)
        for entry in index_tree:
            has_children = bool(entry.get('children'))
            entry['type'] = 'index_only' if has_children else 'folder'
            entry['gen_index'] = True
            for child in entry.get('children', []):
                child['type'] = 'folder'
                child['gen_index'] = True
        print(f"|  [idx] 索引条目   {len(index_tree):<37} |")

    elif index_mode == 'pdf' and index_source:
        print("|  [scan] 索引模式   使用预转换索引 PDF                       |")
        index_dir = Path(tempfile.gettempdir()) / "_idx_pages"
        index_paths = split_index_pdf(Path(index_source), index_dir)
        print(f"|  [idx] 索引页数   {len(index_paths):<37} |")

        items = sorted([d for d in input_dir.iterdir() if d.is_dir() and not should_skip(d.name)],
                       key=lambda x: x.name)
        index_tree = []
        for i, item in enumerate(items):
            if i >= len(index_paths):
                break
            entry = {
                "page_num": i + 1,
                "title": item.name,
                "type": "folder",
                "path": item,
                "index_pdf_path": index_paths[i],
                "children": [],
            }
            subdirs = sorted([d for d in item.iterdir() if d.is_dir() and not should_skip(d.name)],
                             key=lambda x: x.name)
            for j, sub in enumerate(subdirs):
                idx = i + 1 + j + 1
                if idx <= len(index_paths):
                    entry["children"].append({
                        "page_num": idx,
                        "title": sub.name,
                        "type": "folder",
                        "path": sub,
                        "index_pdf_path": index_paths[idx - 1],
                    })
            index_tree.append(entry)

    elif index_mode == 'none':
        print("|  [scan] 索引模式   无索引（直接合并）                        |")
        index_tree = [{
            "page_num": 1,
            "title": input_dir.name,
            "type": "folder",
            "path": input_dir,
            "gen_index": config.get('title_index', True),
            "children": [],
        }]
    else:
        raise ValueError(f"不支持的索引模式: {index_mode}")

    # 预扫描：统计文件
    img_count = 0
    pdf_count = 0
    total_files = 0

    def _count_in_node(node):
        nonlocal img_count, pdf_count, total_files
        node_type = node.get('type', 'folder')
        if node_type == 'folder' and 'path' in node:
            try:
                files = collect_folder(node['path'], config.get('include_tables', False))
            except Exception:
                files = []
            for f in files:
                ext = f.suffix.lower()
                if ext in IMAGE_EXTS:
                    img_count += 1
                elif ext == '.pdf':
                    pdf_count += 1
                total_files += 1
        elif node_type == 'file' and 'path' in node:
            fpath = node['path']
            if fpath.exists():
                ext = fpath.suffix.lower()
                if ext in IMAGE_EXTS:
                    img_count += 1
                elif ext == '.pdf':
                    pdf_count += 1
                total_files += 1
        for child in node.get('children', []):
            _count_in_node(child)

    for entry in index_tree:
        _count_in_node(entry)

    print(f"|  [file] 找到文件   {total_files} 个 (图片 {img_count} + PDF {pdf_count}){' ' * max(0, 15 - len(str(total_files)))} |")
    print("|" + " " * 50 + "|")

    # Phase 2: 处理文件
    progress = {'done': 0, 'total': total_files}
    writer = PdfWriter()
    page_map = {}

    for entry in index_tree:
        _process_node(entry, writer, None, page_map, config, progress)

    print()  # 换行结束进度条

    total_pages = len(writer.pages)

    # Phase 3: 保存临时 + 页码
    tmp_pdf = tempfile.mktemp(suffix='.pdf')
    with open(tmp_pdf, 'wb') as fp:
        writer.write(fp)

    add_page_numbers(tmp_pdf, tmp_pdf)

    # Phase 4: 书签
    if config.get('add_bookmarks', True):
        bms = collect_bookmarks_from_index_tree(index_tree, page_map)
        add_bookmarks(tmp_pdf, bms, tmp_pdf)

    # Phase 5: 输出
    os.makedirs(output_path.parent, exist_ok=True) if output_path.parent != output_path else None
    import shutil
    shutil.copy2(tmp_pdf, output_path)
    os.remove(tmp_pdf)

    elapsed = time.time() - t_start
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    time_str = f"{mins} 分 {secs} 秒" if mins > 0 else f"{secs} 秒"

    print(f"|  [OK] 处理完成   耗时 {time_str}{' ' * max(0, 32 - len(time_str))} |")
    print(f"|  [pages] 总页数     {total_pages} 页{' ' * max(0, 30 - len(str(total_pages)))} |")
    print("+" + "-" * 50 + "+")
    return str(output_path)
