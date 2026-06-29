<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/license-Apache%202.0-blue.svg" alt="Apache 2.0">
  <img src="https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform">
</p>

<h1 align="center">归页 Unipage</h1>
<p align="center"><strong>散落万千，终归一页</strong></p>
<p align="center"><sub>every file finds its place</sub></p>

<p align="center">
  <a href="#quick-start">Quick Start</a> ·
  <a href="#use-cases">Use Cases</a> ·
  <a href="#ai-agent-support">AI Agent</a> ·
  <a href="#security">Security</a> ·
  <a href="#install">Install</a> ·
  <a href="#license">License</a>
</p>

<p align="center">
  <img src="docs/banner.png" alt="归页 Unipage" width="720">
</p>

---

## What is this

**Picture this:** the project is done. All that's left is collecting every file you've accumulated along the way and printing the damn thing. Just one task — and somehow still a pain. Photos are crooked, scans are sideways, PDFs come in every size imaginable. And the real kicker? You organized these files in a structure that made sense to *you at the time*. Two days later, you're already wondering: "Where did I even put that?"

**Unipage handles the last mile.** Organize however you like. Point it at the root folder, and it digs through every corner — follows your structure, sorts your files, trims uniform margins on every page, stamps page numbers, and builds a table-of-contents bookmark tree. What you get back: a clean, print-ready PDF.

> *"Just tidy up this folder for me"* — one sentence, three minutes, done.

---

## Use Cases

Any industry, any material — if you need to turn a pile of scattered files into a clean PDF, Unipage does it. **Every output automatically includes: hierarchical index + collapsible bookmarks + global page numbers + 18mm uniform margins.**

| Domain | What you have | What you get |
|--------|--------------|--------------|
| **Legal due diligence** | Licenses, articles, investment certificates, scanned vouchers | A neatly typeset diligence binder |
| **Financial audit** | Invoices, bank receipts, contracts, reconciliations | An audit workpaper ready for filing |
| **Compliance review** | Permits, approval letters, internal policies, reports | A browseable compliance archive |
| **Project archives** | Blueprints, acceptance forms, meeting minutes | A polished project closeout record |
| **Academic research** | Questionnaires, raw data scans, literature excerpts | A print-friendly research packet |
| **Bids & tenders** | Qualification certificates, performance proofs, financials | A bid compilation that stands out |

<details>
<summary>📊 Before & after</summary>

| 😫 Before | 😎 After |
|---|---|
| Open every file by hand — rotate, resize, repeat | Auto-detect orientation, one-pass adapt |
| Documents print edge-to-edge, content gets clipped | 18mm safe margins on every page |
| Flip through hundreds of pages hunting by eye | Bookmark nav + table of contents, instant jump |
| Spend an afternoon assembling, then realize the page numbers are wrong | Three minutes, numbers dead-on |
| New machine, new project — do it all over again | One command works for archives, audits, bids, anything |

</details>

## What it does for you

| Capability | In plain English |
|------------|-----------------|
| **Auto-index** | Scans your folder tree and builds a hierarchical index — no hand-written table of contents |
| **PDF bookmarks** | Even a thousand pages — click the bookmark and you're there, faster than flipping paper |
| **Smart wrapping** | Images stay proportional, never cropped or stretched. PDFs get the best rendering path automatically — no blur, no skew, no loss |
| **Print-ready** | 18mm margins on every page, landscape/portrait auto-detected. Send straight to the print shop |
| **Fast path first** | 95% of pages take the high-fidelity vector path. Only edge cases fall back to raster |

## Install

```bash
pip install git+https://github.com/bangchuiLee/unipage.git
```

Or clone locally:

```bash
git clone https://github.com/bangchuiLee/unipage.git
cd unipage
pip install .
```

Dependencies:

| Package | Version | Purpose |
|---------|---------|---------|
| PyMuPDF | ≥1.24 | PDF rendering & splitting |
| reportlab | ≥4.0 | Index pages & page numbers |
| pypdf | ≥5.0 | PDF merging & bookmarks |
| Pillow | ≥10.0 | Image processing |
| openpyxl | ≥3.1 | xlsx index reading |

## Quick Start

### Zero config — auto-index

```bash
diligence-pdf assemble ./my-files -o archive.pdf
```

Once it runs, you'll see:

```
$ diligence-pdf assemble ./project-files -o archive.pdf

╭──────────────────────────────────────────────────╮
│  归页 v1.0                                       │
│                                                  │
│  📂 Input dir    ./project-files                  │
│  🔍 Index mode   auto-scan directory              │
│  📑 Index pages  N                                │
│  📄 Files found  N (images A + PDFs B)            │
│                                                  │
│  [████████████████████] 100% (N/N)                │
│                                                  │
│  ✅ Done         X min Y sec                      │
│  📏 Total pages  N                                │
╰──────────────────────────────────────────────────╯
```

<p align="center">
  <img src="docs/pipeline.svg" alt="Processing pipeline" width="800">
</p>

Input structure:

```
project-docs/
  ├── 01-incorporation/
  │   ├── business-license.jpg
  │   ├── articles.pdf
  │   └── shareholder-register/
  │       └── ...
  ├── 02-changes/
  └── ...
```

Folder names become index headings. Subfolders become secondary index entries. Output: one PDF with bookmarks, page numbers, and uniform margins.

### Python API

```python
from diligence_pdf import assemble

assemble({
    "input_dir": "/path/to/documents",
    "output_path": "/path/to/output.pdf",
    "index_mode": "auto",       # auto / pdf / none
    "image_mode": "fit",        # fit / split
    "add_bookmarks": True,
    "add_page_numbers": True,
})
```

### Pre-built index PDF

```python
assemble({
    "input_dir": "/path/to/documents",
    "output_path": "/path/to/output.pdf",
    "index_mode": "pdf",
    "index_source": "/path/to/index.pdf",
})
```

## PDF wrapping decision tree

```
Input PDF page
  │
  ├─ A4 + has margins + no rotation issues → pass-through (vector, zero overhead)
  │
  ├─ Near A4 + no rotation issues → show_pdf_page vector wrap (fast)
  │
  └─ Non-standard size OR rotation issues → 150dpi pixmap render (reliable fallback)
```

## AI Agent support

Unipage is a **pure Python function + CLI** with zero framework dependencies. Any AI agent that can execute Python can call it directly.

| Agent / Platform | How to use |
|---|---|
| **Claude Code** | `pip install .` then `from diligence_pdf import assemble` |
| **Claude Desktop (MCP)** | Expose `assemble()` as a tool via Python MCP server |
| **OpenAI Codex CLI** | Supports `pip install` + function calling, auto-discovers API |
| **ChatGPT (Code Interpreter)** | Upload wheel or `pip install git+URL`, import directly in sandbox |
| **Cursor / Windsurf** | `pip install` in environment, call directly |
| **Aider** | Supports arbitrary Python module imports, no adaptation needed |
| **Gemini CLI** | Standard Python package, `pip install` then import |
| **GitHub Copilot Coding Agent** | Autocomplete suggests `assemble()` after install |
| **Devin** | Standard `pip install`, callable in tasks |

> **Design note**: the entry point `assemble(config: dict) -> str` takes a plain dict — no type annotations required, no async, no side effects. Any agent just constructs a dict and calls it.

## Security

### Zero-network guarantee

Unipage runs **entirely offline**. It does not, and never needs to, make any network requests:

- No API calls
- No telemetry
- No data uploads
- No credential storage
- No third-party services

Run it air-gapped. Packet-capture it. Audit the source — ~1,200 lines of Python, no obfuscation, no dynamic execution.

### Dependency audit

| Dependency | License | Downloads |
|------------|---------|-----------|
| PyMuPDF | AGPL | 50M+ |
| reportlab | BSD | 30M+ |
| pypdf | BSD | 80M+ |
| Pillow | HPND-C | 500M+ |
| openpyxl | MIT | 200M+ |

All dependencies are from the official PyPI registry and their licenses permit local use.

> ⚠️ **Note**: PyMuPDF uses AGPL v3. Local CLI / AI agent invocation does not trigger copyleft terms. For commercial SaaS deployment (network distribution), replace with a pure pypdf solution or consult legal counsel.

## Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `input_dir` | Path | required | Root directory of source documents |
| `output_path` | Path | required | Output PDF path |
| `index_mode` | str | `auto` | `auto` / `pdf` / `none` |
| `index_source` | Path | — | Index PDF (for `pdf` mode) |
| `image_mode` | str | `fit` | `fit` (proportional) / `split` (long image crop) |
| `add_bookmarks` | bool | `true` | PDF bookmarks |
| `add_page_numbers` | bool | `true` | Page numbers |
| `include_tables` | bool | `false` | Attempt xls/xlsx processing |

## License

Apache License 2.0 — see [LICENSE](./LICENSE)

---

<p align="center"><sub>散落万千，终归一页 · every file finds its place</sub></p>
