@echo off
REM start.bat - Windows one-click backend start (development mode)

set PORT=8000

REM If you use a virtual environment, activate it first, e.g.:
REM call .venv\Scripts\activate

uvicorn backend.main:app --reload --port %PORT%
