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
     OPENAI_MODEL=gpt-5-nano

3) 验证 OpenAI 连通性（可选）
   - 运行测试脚本：

     D:\anaconda\Scripts\conda.exe run -p d:\Desktop\ELEC_5620_Final\.conda --no-capture-output python -m backend.openai_test

   - 看到 `OK: pong` 表示 API 可用。

4) 启动后端服务

   D:\anaconda\Scripts\conda.exe run -p d:\Desktop\ELEC_5620_Final\.conda --no-capture-output python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

5) 用法示例
- 健康检查：浏览器打开 http://localhost:8000/health
- 创建工单：`POST /cases` (multipart/form-data)
- 最小分析：`POST /analyze` 表单字段 `issue_description`

## 常见问题

- 401/403：检查 OPENAI_API_KEY 是否有效、是否带 sk- 前缀，环境变量是否被读取（重启终端/VS Code）。
- 429：达到速率/配额限制，可稍后重试或更换模型/提升额度。
- 模型兼容性：我们按通用参数发起调用；个别新模型不支持 temperature/max_tokens，我们已在代码中去除。

## 安全
- 不要将 `.env` 提交到版本库。
- 若 Key 泄露，请在 OpenAI 控制台立即旋转重置。