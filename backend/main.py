"""
FastAPI 应用主入口（最小可运行示例）。

功能：
- /health 健康检查
- /cases 接收收据、商品图片与问题描述，保存到本地 uploads 目录，返回 case_id

说明：为便于快速联调，未引入数据库与鉴权。若在生产环境，请补充鉴权、限流、日志与错误处理。
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import os
import uuid
from .ai_agent import analyze_issue

app = FastAPI(title="ELEC_5620_FINAL Backend")

# 允许本地前端联调
app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)

UPLOAD_ROOT = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_ROOT, exist_ok=True)


@app.get("/health")
async def health():
	return {"status": "ok"}


@app.post("/cases")
async def create_case(
	receipt_files: Optional[List[UploadFile]] = File(default=None),
	product_images: Optional[List[UploadFile]] = File(default=None),
	issue_description: str = Form("")
):
	"""创建工单，保存上传文件与描述，返回 case_id。"""
	case_id = str(uuid.uuid4())
	case_dir = os.path.join(UPLOAD_ROOT, case_id)
	receipts_dir = os.path.join(case_dir, "receipt_files")
	images_dir = os.path.join(case_dir, "product_images")
	os.makedirs(receipts_dir, exist_ok=True)
	os.makedirs(images_dir, exist_ok=True)

	# 保存问题描述
	if issue_description is not None:
		with open(os.path.join(case_dir, "issue_description.txt"), "w", encoding="utf-8") as f:
			f.write(issue_description)

	# 保存收据文件
	if receipt_files:
		for uf in receipt_files:
			content = await uf.read()
			safe_name = uf.filename or "receipt"
			with open(os.path.join(receipts_dir, safe_name), "wb") as f:
				f.write(content)

	# 保存商品图片
	if product_images:
		for uf in product_images:
			content = await uf.read()
			safe_name = uf.filename or "image"
			with open(os.path.join(images_dir, safe_name), "wb") as f:
				f.write(content)

	return JSONResponse({"case_id": case_id, "status": "created"})


@app.post("/analyze")
async def analyze(issue_description: str = Form("")):
	"""直接对问题描述进行最小分析，返回文本建议。"""
	if not issue_description.strip():
		return JSONResponse({"error": "issue_description is required"}, status_code=400)
	result = analyze_issue(issue_description)
	return JSONResponse(result)
