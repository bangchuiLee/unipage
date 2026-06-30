#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主流水线 — 组装索引树 + 文件处理（分段吐盘） + 合并 + 页码 + 书签
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


# ── 分段写盘 ────────────────────────────────────────
CHUNK_SIZE = 300  # 每段最多页数，达到后自动吐盘


class _ChunkWriter:
    """包装 PdfWriter，达到阈值时自动分段写盘，控制内存占用。支持断点续跑。"""

    def __init__(self, chunk_size=CHUNK_SIZE, temp_dir=None, resume_dir=None):
        self._chunk_size = chunk_size
        self._chunks = []       # [(temp_path, page_count), ...]
        self._writer = PdfWriter()
        self._page_base = 0     # 前面已吐盘的页数累计
        self._temp_dir = Path(temp_dir) if temp_dir else Path(tempfile.gettempdir())
        self._temp_dir.mkdir(parents=True, exist_ok=True)
        self._files_done = 0    # 断点续跑：已处理文件数

        # 断点续跑：加载已有分段
        if resume_dir:
            self._load_existing(Path(resume_dir))

    def _load_existing(self, d):
        """从已有分段目录恢复，设置 page_base 和 files_done。损坏的分段自动跳过。"""
        paths = sorted(d.glob("_chunk_*.pdf"))
        if not paths:
            return
        total_pages = 0
        skipped = 0
        for p in paths:
            try:
                r = PdfReader(str(p))
                n = len(r.pages)
                self._chunks.append((str(p), n))
                total_pages += n
            except Exception:
                skipped += 1
                p.unlink()
        self._page_base = total_pages

        # 读取进度文件
        progress_file = d / ".progress"
        if progress_file.exists():
            data = progress_file.read_text().strip().split('\n')
            self._files_done = int(data[0])
            # 有跳过的分段时，保守回退进度
            if skipped > 0 and len(data) > 1:
                total = int(data[1])
                # 每个完整分段约 300 页，估算回退文件数
                est_pages_per_chunk = max(total_pages / len(self._chunks), 300) if self._chunks else 300
                est_files_per_chunk = est_pages_per_chunk * self._files_done / max(total_pages + est_pages_per_chunk * skipped, 1)
                self._files_done = max(0, int(self._files_done - est_files_per_chunk * skipped))

    def save_progress(self, files_done, total):
        """保存进度到临时目录，用于断点续跑。"""
        pf = self._temp_dir / ".progress"
        pf.write_text(f"{files_done}\n{total}\n")

    def add_page(self, page):
        self._writer.add_page(page)
        if len(self._writer.pages) >= self._chunk_size:
            self._flush()

    @property
    def pages(self):
        """当前段内的页面列表"""
        return self._writer.pages

    def global_page(self):
        """当前段内下个页面在最终 PDF 中的全局页码（1-based）"""
        return self._page_base + len(self._writer.pages) + 1

    def _flush(self):
        if len(self._writer.pages) == 0:
            return
        idx = len(self._chunks) + 1
        f = str(self._temp_dir / f"_chunk_{idx:04d}.pdf")
        with open(f, 'wb') as fp:
            self._writer.write(fp)
        n = len(self._writer.pages)
        self._chunks.append((f, n))
        self._page_base += n
        self._writer = PdfWriter()
        # 每吐一段就记录进度（files_done 由外层更新后调用 save_progress）
        if self._files_done > 0:
            self.save_progress(self._files_done, 0)

    def finish(self, output_path):
        """合并所有分段 → 写最终 PDF → 清理分段临时文件。返回总页数。"""
        self._flush()  # 最后一段

        if len(self._chunks) == 0:
            # 没有任何页面
            return 0

        if len(self._chunks) == 1:
            # 只有一段，直接移动
            import shutil
            shutil.copy2(self._chunks[0][0], output_path)
            total = self._chunks[0][1]
        else:
            merger = PdfWriter()
            total = 0
            for path, n in self._chunks:
                merger.append(path)
                total += n
            merger.write(output_path)

        # 清理分段文件和临时目录
        for path, _ in self._chunks:
            try:
                os.remove(path)
            except OSError:
                pass
        try:
            self._temp_dir.rmdir()
        except OSError:
            pass

        return total


# ── 文件处理 ────────────────────────────────────────

def _process_file(filepath, ctx, image_mode='fit', progress=None):
    """处理单个文件，页面加入 _ChunkWriter"""
    fname = filepath.name
    ext = filepath.suffix.lower()

    # 断点续跑：跳过已处理文件
    if progress and progress.get('files_skipped', 0) < progress.get('resume_from', 0):
        progress['files_skipped'] = progress.get('files_skipped', 0) + 1
        if progress['files_skipped'] == 1:
            print(f"  [resume] 跳过前 {progress['resume_from']} 个已处理文件...")
        if progress['files_skipped'] == progress['resume_from']:
            print(f"  [resume] 完成，继续处理剩余文件")
        return

    if ext in IMAGE_EXTS:
        try:
            if image_mode == 'split':
                chunks = split_image_pages(str(filepath))
                for chunk_img, is_landscape in chunks:
                    buf = chunk_to_page(chunk_img, is_landscape)
                    ctx.add_page(PdfReader(buf).pages[0])
            else:
                buf = image_to_page(str(filepath))
                ctx.add_page(PdfReader(buf).pages[0])
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
                    ctx.add_page(pg)
            except Exception as e:
                print(f"\n  [SKIP] {fname} p{pn+1}: {e}")
        src.close()

    elif ext in TABLE_EXTS:
        pdf_sibling = filepath.with_suffix('.pdf')
        if pdf_sibling.exists():
            pass
        else:
            try:
                result = format_xlsx(str(filepath))
                formatted = result["path"]
                sheets_info = ", ".join(
                    f"{s['name']}({s['rows']}行×{s['cols']}列,{s['orientation']})"
                    for s in result["sheets"]
                )
                print(f"\n  [XLSX] {fname} 已格式化 -> {Path(formatted).name}")
                print(f"         请用 Excel 打开 -> Ctrl+P 打印为 PDF，放回原目录")
                print(f"         共 {len(result['sheets'])} 个 sheet: {sheets_info}")
            except Exception as e:
                print(f"\n  [XLSX] {fname}: 格式化失败 ({e})，请手动转换为 PDF")

    if progress is not None:
        progress['done'] += 1
        ctx._files_done = progress['done']  # 同步到 ChunkWriter，用于断点进度保存
        _update_progress_bar(progress)


def _update_progress_bar(progress):
    """刷新进度条显示——PowerShell 兼容，每 10 个文件或整百分比时输出一行"""
    done = progress['done']
    total = progress['total']
    pct = done * 100 // total if total > 0 else 100
    bar = '#' * (pct // 5) + '.' * (20 - pct // 5)
    if done % 10 == 0 or done == total:
        print(f"  [{bar}] {pct}% ({done}/{total})")


def _process_node(node, ctx, index_paths, page_map, config, progress=None):
    """处理索引树节点（递归），页面加入 _ChunkWriter"""
    image_mode = config.get('image_mode', 'fit')
    page_map[node['page_num']] = ctx.global_page()

    # 索引页
    if node.get('index_pdf_path'):
        r = PdfReader(node['index_pdf_path'])
        ctx.add_page(r.pages[0])
    elif node.get('gen_index'):
        buf = make_index_page(node['title'], node.get('font_size', 16), node.get('alignment', 'left'))
        ctx.add_page(PdfReader(buf).pages[0])

    # 内容
    node_type = node.get('type', 'folder')
    if node_type == 'folder':
        files = collect_folder(node['path'], config.get('include_tables', False))
        for f in files:
            _process_file(f, ctx, image_mode, progress)

    elif node_type == 'file':
        if node['path'].exists():
            _process_file(node['path'], ctx, image_mode, progress)

    elif node_type == 'index_only':
        pass

    # 子节点
    for child in node.get('children', []):
        _process_node(child, ctx, index_paths, page_map, config, progress)


# ── 主入口 ──────────────────────────────────────────

def assemble(config):
    """
    主入口。
    config 必需: input_dir, output_path
    config 可选: index_mode, index_source, image_mode, margin,
                 add_bookmarks, add_page_numbers, include_tables, chunk_size
    """
    input_dir = Path(config['input_dir'])
    output_path = Path(config['output_path'])
    t_start = time.time()

    print("+" + "-" * 48 + "+")
    print(f"|  Unipage v1.0{' ' * 33}|")
    print("|" + " " * 48 + "|")
    print(f"|  [dir] {str(input_dir)[:38]:<38} |")

    # Phase 1: 构建索引树
    index_mode = config.get('index_mode', 'auto')
    index_source = config.get('index_source')

    if index_mode == 'auto':
        print("|  [scan] 自动扫描目录生成索引                          |")
        index_tree = auto_index_from_folders(input_dir)
        for entry in index_tree:
            has_children = bool(entry.get('children'))
            entry['type'] = 'index_only' if has_children else 'folder'
            entry['gen_index'] = True
            for child in entry.get('children', []):
                child['type'] = 'folder'
                child['gen_index'] = True
        print(f"|  [idx] {len(index_tree)} 个索引条目{' ' * (36 - len(str(len(index_tree))))} |")

    elif index_mode == 'pdf' and index_source:
        print("|  [scan] 使用预转换索引 PDF                             |")
        index_dir = Path(tempfile.gettempdir()) / "_idx_pages"
        index_paths = split_index_pdf(Path(index_source), index_dir)
        print(f"|  [idx] {len(index_paths)} 页{' ' * (38 - len(str(len(index_paths))))} |")

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
        print("|  [scan] 无索引（直接合并）                            |")
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

    print(f"|  [file] {total_files} 个 (图片 {img_count} + PDF {pdf_count}){' ' * max(0, 17 - len(str(total_files)))} |")
    print("|" + " " * 48 + "|")

    # Phase 2: 处理文件（分段吐盘，支持断点续跑）
    chunk_temp_dir = output_path.parent / "_chunks"
    resume_dir = config.get('resume_chunks')  # 断点续跑：已有分段目录
    resume_from = 0

    if resume_dir:
        # 从进度文件读取已完成的文件数
        pf = Path(resume_dir) / ".progress"
        if pf.exists():
            data = pf.read_text().strip().split('\n')
            resume_from = int(data[0])

    progress = {'done': resume_from, 'total': total_files, 
                'files_skipped': 0, 'resume_from': resume_from}
    ctx = _ChunkWriter(config.get('chunk_size', CHUNK_SIZE), 
                       temp_dir=chunk_temp_dir, resume_dir=resume_dir)
    page_map = {}

    for entry in index_tree:
        _process_node(entry, ctx, None, page_map, config, progress)

    # 保存最终进度
    ctx.save_progress(progress['done'], total_files)

    print()

    # Phase 3: 合并分段 → 写输出
    print("|  [merge] 合并分段...                                    |")
    total_pages = ctx.finish(output_path)

    # Phase 4: 页码 + 书签
    add_page_numbers(output_path, output_path)

    if config.get('add_bookmarks', True):
        bms = collect_bookmarks_from_index_tree(index_tree, page_map)
        add_bookmarks(output_path, bms, output_path)

    elapsed = time.time() - t_start
    mins = int(elapsed // 60)
    secs = int(elapsed % 60)
    time_str = f"{mins} 分 {secs} 秒" if mins > 0 else f"{secs} 秒"

    print(f"|  [OK] {time_str}{' ' * (42 - len(time_str))} |")
    print(f"|  [pages] {total_pages} 页{' ' * (37 - len(str(total_pages)))} |")
    print("+" + "-" * 48 + "+")
    return str(output_path)
