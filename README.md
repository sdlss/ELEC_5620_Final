# ELEC-5620-Final
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

   ## Workflow
   1. Start backend service
   2. start frontend service:
      - login page
      - index page (create new case)
      - upload receipt, description
      - ocr, issue classification, analysis report (completed by backend service)
      - result page

   ## Recover after unzip
   - cd D:\Desktop\ELEC_5620_Final (replace with your own file path) 
   - D:\anaconda\Scripts\conda.exe run -p D:\Desktop\ELEC_5620_Final\.conda --no-capture-output python -m pip install -r D:\Desktop\ELEC_5620_Final\backend\requirements.txt (replace with your own file path)
   -  Create the backend .env file (put the following information in this file)
      OPENAI_API_KEY=sk-xxxx
      OPENAI_MODEL=gpt-4o-mini
   - D:\anaconda\Scripts\conda.exe run -p d:\Desktop\ELEC_5620_Final\.conda --no-capture-output uvicorn backend.main:app --host 127.0.0.1 --port 8000 // replace the file path with your own (run this command to start your backend service)

   - cd D:\Desktop\ELEC_5620_Final\frontend (replace with your own file path)
   - npm install
   - create .env.local file : NEXT_PUBLIC_API_BASE_URL=http://127.0.0.1:8000
   - npm run dev
   - login information: 123@163.com   password:123456   

    ## Database-backed login (optional but recommended)
    - Import schema if not already done: run the SQL in `final5620.sql` into your PostgreSQL database.
    - Ensure your backend has access to the DB via `DATABASE_URL` in `.env` (either repo root or `backend/.env`).
    - Create a user in `app_user` using the helper:
       - D:\anaconda\Scripts\conda.exe run -p D:\Desktop\ELEC_5620_Final\.conda --no-capture-output python -m backend.create_user --email you@example.com --password YourPass123 --role consumer
    - In the frontend, open `http://127.0.0.1:3000/login`, sign in with the email/password above.
    - On success, you'll be redirected to the dashboard with a stored token.