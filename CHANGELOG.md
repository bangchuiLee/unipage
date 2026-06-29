# Changelog

## [1.0.0] — 2026-06-29

### Added

- 自动索引模式：扫描目录结构自动生成层级索引
- PDF 书签（大纲）生成，支持多层级可折叠
- PDF 智能包裹三路决策树：原样通过 → 矢量包裹 → pixmap 回退
- 图片等比缩放模式（fit）和长图切分模式（split）
- macOS 资源分叉（`._`）自动过滤
- WorkBuddy Skill 集成
- CLI 入口 `assembler.py`

### Verified

- 横版/纵版 PDF 自动适配
- 旋转图像异常 PDF 自动回退到光栅化
- 500+ 文件、1500+ 页大规模项目
- 打印就绪 18mm 页边距
