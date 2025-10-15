# ELEC-5620-Final

基于“电商维权助手”场景的前后端分离项目骨架。当前版本已提供最小可运行的后端与前端上传页面（未初始化完整 React/Next.js 工程），支持：
- 上传收据文件（图片/PDF）
- 上传商品图片
- 填写问题描述
- 后端存储上传内容并返回 case_id

## 目录结构

```
ELEC_5620_FINAL/
├── frontend/                    # 前端（示例页面与API封装）
│   ├── public/
│   └── src/
│       ├── pages/
│       │   ├── index.tsx       # 首页占位（注释/可扩展）
│       │   ├── upload.tsx      # 上传表单（最小可用）
│       │   └── result.tsx      # 结果展示页占位
│       └── utils/
│           └── api.ts          # 与后端交互封装（最小可用）
└── backend/                    # FastAPI 后端
		├── main.py                 # 应用入口，含 /health 与 /cases
		├── ai_agent.py             # AI 调用逻辑占位
		├── config.py               # 配置占位
		├── prompts/                # Prompt 模板
		│   ├── receipt_extraction.txt
		│   ├── issue_analysis.txt
		│   ├── policy_check.txt
		│   └── communication.txt
		├── uploads/                # 上传文件保存目录（自动创建）
		├── requirements.txt        # 后端依赖
		└── README.md               # 后端说明占位

start.bat                       # Windows 一键启动后端
```

## 后端运行（Windows）

1. 建议创建并激活虚拟环境（可选）
2. 安装依赖
3. 启动服务

你也可以直接双击或在命令行执行根目录下的 `start.bat`，默认端口 8000。

健康检查：打开 http://localhost:8000/health 应返回 `{ "status": "ok" }`。

## 已实现接口（最小集）

- `GET /health`
	- 作用：健康检查
	- 返回：`{ status: "ok" }`

- `POST /cases`（multipart/form-data）
	- 字段：
		- `receipt_files[]`: 收据文件（可多文件；图片或PDF）
		- `product_images[]`: 商品图片（可多文件）
		- `issue_description`: 问题描述（字符串）
	- 行为：保存到 `backend/uploads/{case_id}/...` 并返回 `case_id`
	- 返回：`{ case_id: string, status: "created" }`

## 前端现状

- `upload.tsx` 提供最小上传表单并调用后端 `/cases`。
- 当前仓库尚未完成完整的 React/Next.js 初始化，因此在前端文件中临时使用了 `// @ts-nocheck` 以绕过类型检查。
- 如需我继续：
	- 初始化 Next.js 工程（package.json、tsconfig、路由等）并迁移现有页面
	- 完成 `result.tsx` 展示与路由跳转
	- 丰富交互与状态管理、错误提示

## 后续工作建议

1. OCR/解析：支持从收据图片/PDF中抽取文本（Tesseract、PyMuPDF、pdfminer.six或云端OCR）。
2. AI 调用：在 `ai_agent.py` 串联 prompts（抽取→问题分析→政策对照→沟通话术），并暴露 `/analyze` 接口。
3. 策略/规则：若需对平台政策或法规进行匹配，准备文本语料，后续可接入向量检索（RAG）。
4. 前端工程化：初始化 Next.js，完善页面路由与结果展示。
5. 配置与安全：通过 `.env` 管理密钥（如 OPENAI_API_KEY），启用限流与日志。
6. 测试与验证：添加最小单测/集成测试，保证上传与分析链路稳定。

## 备注

- 后端依赖见 `backend/requirements.txt`，启动脚本为根目录 `start.bat`。
- 上传文件默认保存在 `backend/uploads/`，请注意磁盘配额与清理策略。
- 如需更改后端端口或跨域，请在 `backend/main.py` 中调整。

---

目前的文件内容是copilot自动生成的，需更改。