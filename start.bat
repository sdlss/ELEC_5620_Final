@echo off
REM start.bat - Windows 一键启动后端（开发模式）

set PORT=8000

REM 如有虚拟环境，请先激活，例如：
REM call .venv\Scripts\activate

uvicorn backend.main:app --reload --port %PORT%
