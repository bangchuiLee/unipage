#!/usr/bin/env python3
"""CLI entry: python -m diligence_pdf assemble /path/to/dir -o out.pdf"""

import argparse
import sys
from pathlib import Path

from diligence_pdf import assemble


def main():
    p = argparse.ArgumentParser(prog="diligence-pdf", description="归页 Unipage · 文档汇集 PDF 工具")
    sub = p.add_subparsers(dest="cmd")

    a = sub.add_parser("assemble", help="合并文件夹为 PDF")
    a.add_argument("input_dir", help="输入根目录")
    a.add_argument("-o", "--output", required=True, help="输出 PDF 路径")
    a.add_argument("--index-mode", default="auto", choices=["auto", "pdf", "none"])
    a.add_argument("--index-source", help="预转换索引 PDF 路径（pdf 模式）")
    a.add_argument("--image-mode", default="fit", choices=["fit", "split"])
    a.add_argument("--no-bookmarks", action="store_true")
    a.add_argument("--no-pagenum", action="store_true")

    args = p.parse_args()
    if args.cmd != "assemble":
        p.print_help()
        sys.exit(1)

    config = {
        "input_dir": Path(args.input_dir),
        "output_path": Path(args.output),
        "index_mode": args.index_mode,
        "index_source": Path(args.index_source) if args.index_source else None,
        "image_mode": args.image_mode,
        "add_bookmarks": not args.no_bookmarks,
        "add_page_numbers": not args.no_pagenum,
    }
    assemble(config)


if __name__ == "__main__":
    main()
