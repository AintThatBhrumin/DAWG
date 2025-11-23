🐾 DAWG — AI Invoice Extractor
FastAPI • React • PostgreSQL • Tailwind • LM Studio (Qwen-VL / Any Local LLM)

🚀 Overview

DAWG is an offline, industry-ready AI Invoice Extraction System built using:

FastAPI backend

React + Tailwind frontend

PostgreSQL database

LM Studio (Qwen-VL / any LLM) for local, private invoice parsing

DAWG converts PDFs, images, or raw text into clean structured JSON, ready for accounting, GST billing, automation, or ERP integration.

⭐ Features
🔍 AI Invoice Parsing

Extracts:

Invoice Number

Date

Vendor Name

Buyer Name

GST Number

Currency

Subtotal

Tax

Total

Line Items (name, qty, unit price, total price)

📎 Supported Input Formats

PDF

JPG / PNG images

Raw text

🤖 AI Engine (Offline)

Uses LM Studio

Works with Qwen-VL, LLaMA, Phi, Gemma, etc.

No internet required

Strict JSON output

🗄️ Database

PostgreSQL

SQLAlchemy ORM

Invoice + Items tables

Auto-creates tables on startup

🎨 Frontend

React 18 + Vite

Tailwind CSS

PDF/Image upload

JSON Pretty Viewer

Copy to Clipboard

Fully responsive

📁 Project Structure
dawg/
│── backend/
│   ├── ai_extractor.py
│   ├── database.py
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── utils/
│   └── requirements.txt
│
│── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── tailwind.config.js
│   └── vite.config.js
│
└── README.md

⚙️ Backend Setup
1️⃣ Create virtual environment
cd backend
python -m venv venv
venv/Scripts/activate

2️⃣ Install dependencies
pip install -r requirements.txt

3️⃣ Create .env
DATABASE_URL=postgresql+psycopg2://postgres:password@localhost:5432/dawg
LMSTUDIO_CHAT_URL=http://127.0.0.1:1234/v1/chat/completions

4️⃣ Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE dawg;"

5️⃣ Run backend
uvicorn main:app --reload


Backend:
👉 http://127.0.0.1:8000

🎨 Frontend Setup
1️⃣ Install dependencies
cd frontend
npm install

2️⃣ Create .env
VITE_API_BASE_URL=http://localhost:8000

3️⃣ Run frontend
npm run dev


Frontend:
👉 http://localhost:5173

🧪 Test API (Windows cURL)
curl.exe -X POST "http://127.0.0.1:8000/invoices/extract" ^
  -H "accept: application/json" ^
  -F "file=@C:/Users/YourName/Downloads/invoice.pdf;type=application/pdf"

🚀 Production Build
Build frontend
npm run build

Need Full Docker Setup?

Ask anytime — I will generate a complete docker-compose.yml to deploy DAWG on a server.

🗺️ Roadmap (Upcoming Features)

🔐 Authentication (JWT)

📊 Invoice history dashboard

✏️ Editable extracted fields

🔁 Multi-model fallback (Qwen → GPT → Claude)

🌐 Auto-detect invoice language

👤 Role-based access

☁️ Deployment templates (Render / Railway / Vercel)

🤝 Contributing

Pull requests are welcome.
Please open an issue before submitting major changes.

📜 License

MIT License © 2025 Bhrumin Madhu
