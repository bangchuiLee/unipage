# Security Policy

## 安全承诺

本工具**完全本地运行**，不会：

- 发起任何网络请求
- 上传或收集用户数据
- 读取输出目录以外的文件
- 使用任何 API Key、密码或凭据

## 依赖项

所有依赖均为 PyPI 官方包，累计下载量超过 5000 万次：

| 包 | 用途 | 许可证 | 风险 |
|----|------|--------|------|
| PyMuPDF | PDF 读写/渲染 | AGPL | 商用注意 |
| reportlab | PDF 生成 | BSD | 无 |
| pypdf | PDF 合并/书签 | BSD | 无 |
| Pillow | 图片处理 | HPND-C | 无 |
| openpyxl | xlsx 读取 | MIT | 无 |

> **注意**：PyMuPDF 使用 AGPL 协议。本地 CLI 使用不受影响。如需商用 SaaS 部署，请咨询法律顾问或替换为 pypdf-only 方案。

## 报告漏洞

请通过 [GitHub Issues](https://github.com/superle/diligence-pdf/issues) 报告安全问题。如涉及敏感信息，请私密提交或邮件联系。

## 支持版本

| 版本 | 支持状态 |
|------|----------|
| 1.0.x | ✅ 活跃支持 |
