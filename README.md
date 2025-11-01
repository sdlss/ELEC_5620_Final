# ELEC-5620-Final

电商维权助手（最小可运行骨架）。当前版本后端仅使用 OpenAI 公共 API（不依赖 Azure），已提供：

- `GET /health` 健康检查
- `POST /cases` 上传收据与描述，返回 `case_id`
- `POST /analyze` 最小问题分析（走 OpenAI Chat Completions）

## 目录结构

```
ELEC_5620_FINAL/
├── frontend/                    # 前端（示例页面与API封装）
│   ├── public/
│   └── src/
│       ├── pages/
│       │   ├── index.tsx
│       │   ├── upload.tsx
│       │   └── result.tsx
│       └── utils/
│           └── api.ts
└── backend/                    # FastAPI 后端
    ├── main.py                 # 应用入口 (/health, /cases, /analyze)
    ├── ai_agent.py             # AI 调用（OpenAI 公共 API）
    ├── config.py               # 仅 OpenAI 配置 (OPENAI_API_KEY/OPENAI_MODEL)
    ├── openai_test.py          # OpenAI 连通性测试脚本
    ├── prompts/                # Prompt 模板（占位）
    ├── uploads/                # 上传文件保存目录
    ├── requirements.txt        # 后端依赖
    └── README.md               # 后端说明

start.bat                       # Windows 一键启动后端（可选）
```

## 快速开始（Windows）

1) 安装依赖（已完成可跳过）
   - 我们已在项目内置 Conda 环境安装依赖：`backend/requirements.txt`

2) 配置环境变量
   - 在仓库根目录创建 `.env`，内容示例：

     OPENAI_API_KEY=sk-xxxx
     OPENAI_MODEL=gpt-4o-mini

3) 验证 OpenAI 连通性（可选）
   - 运行测试脚本：

     D:\anaconda\Scripts\conda.exe run -p d:\Desktop\ELEC_5620_Final\.conda --no-capture-output python -m backend.openai_test

   - 看到 `OK: pong` 表示 API 可用。

4) 启动后端服务

   D:\anaconda\Scripts\conda.exe run -p d:\Desktop\ELEC_5620_Final\.conda --no-capture-output python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

5) 用法示例
- 创建工单：`POST /cases` (multipart/form-data)
- 最小分析：`POST /analyze` 表单字段 `issue_description`

## 常见问题

- 401/403：检查 OPENAI_API_KEY 是否有效、是否带 sk- 前缀，环境变量是否被读取（重启终端/VS Code）。
- 429：达到速率/配额限制，可稍后重试或更换模型/提升额度。
- 模型兼容性：我们按通用参数发起调用；个别新模型不支持 temperature/max_tokens，我们已在代码中去除。

## 安全
- 不要将 `.env` 提交到版本库。
- 若 Key 泄露，请在 OpenAI 控制台立即旋转重置。

---

## 近期更新（2025-10-24）

后端（FastAPI）
- 健康检查增强：`GET /health` 返回运行时、配置、存储、CORS 信息；支持 `?deep=true` 尝试轻量 OpenAI 连通性检查。
- 工单创建扩展：`POST /cases` 现在支持直接提供 `receipt_id`（无需上传收据文件），会在本地 uploads 中记录该 ID；引入内存状态机，统一返回 `status/timestamps/progress_percent`。
- 分析流程标准化：`POST /analyze` 接受 `case_id`，在开始/结束时更新状态并把 `status/timestamps/progress_percent` 附加到响应；未提供 `case_id` 时返回一次性完成状态（progress 100）。
- 新增模块：`backend/status.py` 简易内存状态机（case_created → analyzing_issue → analysis_completed）。
- 冒烟测试：
   - `python -m backend.smoke_status` 验证 /cases + /analyze 基本状态流。
   - `python -m backend.smoke_receipt_id` 验证携带 `receipt_id` 的新路径与最终状态字段。

前端（Next.js）
- Upload 页面：将“收据文件上传”改为“填写 Receipt ID”，仍可上传商品图片；提交后串联调用 `/cases` 与 `/analyze`，并把 `status/progress/timestamps` 一并持久化至 localStorage。
- Dashboard：保留状态徽章与（若有）进度条显示；右侧 Quick View 从本地历史读取最近案例；结果页显示 `analysis/key_points/steps`。
- API 封装：`analyzeIssue(issue_description, case_id?)` 支持传入 `case_id`，便于在响应中拿到标准状态字段。

配置与启动
- `.env` 仍采用 OPENAI 公共 API：
   - 必填：`OPENAI_API_KEY`
   - 可选：`OPENAI_MODEL`（默认 `gpt-5-nano`，可按你账号可用模型调整，如 `gpt-4o-mini`）
   - 可选：`OPENAI_BASE_URL`
- 启动后端（开发）：
   - 方式一：双击或运行 `start.bat`
   - 方式二（显式命令）：

      D:\anaconda\Scripts\conda.exe run -p d:\Desktop\ELEC_5620_Final\.conda --no-capture-output python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

说明：如果模型不可用或 Key 缺失，`/health?deep=true` 可能显示 `degraded`，但基本路由仍可用。

## 近期更新（2025-10-22）

- 首页重构为 User Dashboard：
   - 顶部标题与说明，快速入口 “Create New Case”。
   - 快速统计卡片：Latest Case、Status（原 Model 改为 Status）。
   - 右侧 “Quick View”：展示最近多个 case（来自本地历史），可一键打开查看详情。
- 上传页 UI 美化：
   - 自定义文件选择（隐藏原生 input），支持拖拽上传、文件摘要展示、清空按钮。
   - 统一按钮样式，表单布局更清晰。
- 结果页展示结构化信息（analysis/key_points/steps）。
- 前端移除了 health check 按钮与相关代码（后端 `/health` 接口仍可用于手动排查）。
- 新增前端最小运行配置：`frontend/package.json`、`frontend/next.config.mjs`。
- 本地数据持久化：
   - `localStorage.lastAnalysis` 最近一次分析。
   - `localStorage.analysisHistory` 历史列表（最多 50 条）。
   - 历史项包含：`case_id`、`analysis`、`created_at`、`status`（当前为前端标记的 "Analyzed"）。

## 前端运行（Next.js）

1) 安装依赖

```cmd
cd D:\Desktop\ELEC_5620_Final\frontend
npm install
```

2) 配置后端地址（可选）

在 `frontend/.env.local` 写入：

```
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

3) 启动开发服务器

```cmd
npm run dev
```

打开 http://localhost:3000 访问前端。

## 使用流程（端到端）

1) 首页（User Dashboard）：
    - 查看最近一次分析与历史列表（Quick View）。
    - 点击历史条目可直达结果页。
2) 上传页（Upload）：
    - 选择收据/商品图片并填写问题描述，提交后：
       - 前端调用 `POST /cases` 创建工单（返回 `case_id`）。
       - 前端调用 `POST /analyze` 请求 AI 分析。
       - 结果写入 localStorage 的 `lastAnalysis` 与 `analysisHistory`，再跳转 Result 页面。
3) 结果页（Result）：展示模型原始输出与结构化字段（key_points、steps）。

备注：仪表盘 “Status” 当前为前端标记的进度（分析完成后记为 "Analyzed"）。如需精准进度，请扩展后端持久化与状态流转。

## API 契约补充

- `POST /cases`（multipart/form-data）
   - 入参：`receipt_files[]`、`product_images[]`、`issue_description`
   - 出参：`{ case_id: string, status: "created" }`

- `POST /analyze`（application/x-www-form-urlencoded）
   - 入参：`issue_description: string`
   - 出参：
      ```json
      {
         "model": "gpt-5-nano",
         "issue_description": "...",
         "analysis": "...",
         "key_points": ["..."],
         "steps": ["..."]
      }
      ```

   ---

   ## 上传PDF前启动后端
   D:\anaconda\Scripts\conda.exe run -p d:\Desktop\ELEC_5620_Final\.conda --no-capture-output uvicorn backend.main:app --host 127.0.0.1 --port 8000

   ## 调试接口
    http://127.0.0.1:8000/docs

   ## English Version

   ### Overview

   This is a minimal, working skeleton of an e-commerce after-sales assistant. The backend uses the public OpenAI API (no Azure dependency). It supports a small workflow to create a case and run an issue analysis, and ships with a simple Next.js frontend.

   Backend endpoints:
   - GET /health — Health check (kept for manual diagnostics; the UI doesn’t call it anymore)
   - POST /cases — Upload receipts/images and issue description, returns case_id
   - POST /analyze — Minimal analysis using OpenAI Chat Completions

   Frontend pages:
   - index.tsx — User Dashboard: latest analysis, Status card (Model → Status), and a Quick View history list
   - upload.tsx — Upload page with custom file picker (buttons + drag-and-drop), file summary, unified buttons
   - result.tsx — Result page rendering raw model output and structured fields (key_points, steps)

   ### What’s New (2025-10-22)

   - Dashboard redesign (User Dashboard)
      - Header with quick entry “Create New Case”
      - Quick stats: Latest Case, Status (replacing Model)
      - “Quick View” shows multiple recent cases from local history; click to open details
   - Upload page UI refresh
      - Custom file picker (hides native input), drag-and-drop, file summary, clear buttons
      - Consistent button styling and cleaner layout
   - Result page renders structured info (analysis/key_points/steps)
   - Removed frontend health-check button; backend /health remains
   - Minimal frontend setup added: frontend/package.json, frontend/next.config.mjs
   - Local persistence
      - localStorage.lastAnalysis — the most recent analysis
      - localStorage.analysisHistory — up to 50 entries (case_id, analysis, created_at, status)

   ### Project Structure

   ```
   ELEC_5620_Final/
   ├── frontend/
   │   ├── package.json
   │   ├── next.config.mjs
   │   ├── public/
   │   └── src/
   │       ├── pages/
   │       │   ├── index.tsx
   │       │   ├── upload.tsx
   │       │   └── result.tsx
   │       └── utils/
   │           └── api.ts
   └── backend/
         ├── main.py        # /health, /cases, /analyze
         ├── ai_agent.py    # OpenAI API call, returns structured JSON when possible
         ├── config.py      # OPENAI_API_KEY / OPENAI_MODEL / optional OPENAI_BASE_URL
         ├── openai_test.py # connectivity test
         ├── prompts/
         ├── uploads/
         ├── requirements.txt
         └── README.md

   start.bat              # Windows helper to start backend (dev)
   ```

   ### Getting Started (Windows)

   Backend (FastAPI)
   1) Install deps

   ```cmd
   cd D:\Desktop\ELEC_5620_Final
   pip install -r backend\requirements.txt
   ```

   2) Create .env in repo root

   ```
   OPENAI_API_KEY=sk-xxxx
   # Optional:
   # OPENAI_MODEL=gpt-4o-mini
   # OPENAI_BASE_URL=https://api.openai.com/v1
   ```

   3) Start backend (dev)

   ```cmd
   start.bat
   ```

   Default: http://localhost:8000

   Frontend (Next.js)
   1) Install deps

   ```cmd
   cd D:\Desktop\ELEC_5620_Final\frontend
   npm install
   ```

   2) Configure backend base URL (optional)

   Create `frontend/.env.local`:

   ```
   NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

   3) Start dev server

   ```cmd
   npm run dev
   ```

   Visit http://localhost:3000.

   ### End-to-End Flow

   1) Dashboard shows the latest analysis and history. Click an item to open the result.
   2) On the Upload page, select receipts/images and fill in the description, then submit:
       - UI calls POST /cases to create a case (returns case_id)
       - Then calls POST /analyze to run AI analysis
       - The result is saved to localStorage (lastAnalysis and analysisHistory) and the UI navigates to the Result page
   3) Result page shows raw analysis plus structured fields (key_points, steps)

   Note: The Dashboard “Status” is currently a front-end marker (set to “Analyzed” after analysis completes). For precise progress tracking, extend backend persistence and state transitions.

   ### API Contract (Brief)

   - POST /cases (multipart/form-data)
      - In: receipt_files[], product_images[], issue_description
      - Out: `{ case_id: string, status: "created" }`

   - POST /analyze (application/x-www-form-urlencoded)
      - In: `issue_description: string`
      - Out:
         ```json
         {
            "model": "gpt-4o-mini",
            "issue_description": "...",
            "analysis": "...",
            "key_points": ["..."],
            "steps": ["..."]
         }
         ```

   - GET /health → `{ status: "ok" }`

   ### Troubleshooting

   - 401/403: Check OPENAI_API_KEY and ensure the process is loading .env (restart terminal/VS Code)
   - 429: Rate/Quota limits — retry later, switch model, or increase quota
   - Model compatibility: We use a minimal parameter set to avoid unsupported options (e.g., temperature/max_tokens on certain models)
   - Dashboard not updating: It reads from localStorage; submit a new analysis or clear local data (Dashboard buttons)

   ### Security

   - Do not commit `.env` to version control
   - Rotate your API key immediately if it’s leaked


   ## Workflow
   1. Start backend service
   2. start frontend service:
      - login page
      - index page (create new case)
      - upload receipt, description
      - ocr, issue classification, analysis report (completed by backend service)
      - result page

   ## Recover after unzip
   - cd D:\Desktop\ELEC_5620_Final
   - py -3 -m venv .venv
   - .venv\Scripts\activate
   - pip install -r backend\requirements.txt
   -  Create the backend .env file (put the following information in this file)
      OPENAI_API_KEY=sk-xxxx
      OPENAI_MODEL=gpt-4o-mini
   - D:\anaconda\Scripts\conda.exe run -p d:\Desktop\ELEC_5620_Final\.conda --no-capture-output uvicorn backend.main:app --host 127.0.0.1 --port 8000 // replace the file path with your own (run this command to start your backend service)

   - cd D:\Desktop\ELEC_5620_Final\frontend
   - npm install
   - create .env.local file : NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
   - npm run dev