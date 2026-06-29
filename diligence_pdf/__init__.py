#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
diligence-pdf — 尽调底稿 PDF 汇集
==================================
用法:
  python -m diligence_pdf assemble /path/to/dir -o output.pdf
  python -m diligence_pdf assemble /path/to/dir --index-mode auto -o output.pdf

AI Agent 用法:
  from diligence_pdf import assemble
  assemble({"input_dir": "...", "output_path": "..."})
"""

import sys
import os

# Ensure scripts dir is importable
_HERE = os.path.dirname(os.path.abspath(__file__))
_PARENT = os.path.dirname(_HERE)
if _PARENT not in sys.path:
    sys.path.insert(0, _PARENT)

from scripts.assembler import assemble  # noqa: E402

__all__ = ["assemble"]
__version__ = "1.0.0"
