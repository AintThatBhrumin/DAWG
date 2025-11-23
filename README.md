🐾 DAWG — AI Invoice Extractor

![FastAPI](https://img.shields.io/badge/FastAPI-005571?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-20232a?logo=react&logoColor=61DAFB)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?logo=postgresql&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

FastAPI + PostgreSQL + React + Tailwind + Qwen-VL (LM Studio)

DAWG is a fully offline, industry-ready AI-powered Invoice Extraction System designed to convert PDFs, images, or raw text into structured invoice data with high accuracy.

It features a modern React UI, FastAPI backend, PostgreSQL database, and an LLM running locally via LM Studio.



📦 Features

🔍 AI Invoice Parsing

Extracts:

Invoice Number

Date

Vendor Name

Buyer Name

GST Number

Subtotal, Tax, Total

Currency

Line Items with quantity, unit price, total price



📎 Input Formats

PDF

Images (JPG / PNG)

Raw text


🤖 AI Engine

Uses Qwen-VL 4B or any LM Studio model

Fully offline

Custom extraction prompts

JSON only output



🗄️ Database

PostgreSQL with SQLAlchemy ORM

Invoice + Items tables

Auto-create tables on startup



🎨 Frontend

React 18 + Vite

Tailwind CSS

File upload

Pretty invoice table

Expandable JSON viewer

Copy to clipboard




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

venv\Scripts\activate


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

1️⃣ Install Node modules

cd frontend

npm install


2️⃣ Create .env in frontend/

VITE_API_BASE_URL=http://localhost:8000


3️⃣ Run frontend

npm run dev


Frontend:

👉 http://localhost:5173


🧪 Testing the API

Windows cURL:

curl.exe -X POST "http://127.0.0.1:8000/invoices/extract" ^
  -H "accept: application/json" ^
  -F "file=@C:/Users/YourName/Downloads/invoice.pdf;type=application/pdf"


🚀 Production Build

Build frontend:

npm run build


(Optional) Docker support

Ask me and I’ll generate a full docker-compose production setup.




🗺️ Roadmap (Upcoming Features)

 Authentication (JWT)
 
 Invoice history dashboard
 
 Editable extracted fields
 
 Multi-model fallback (Qwen → GPT → Claude)
 
 Auto-detect invoice language
 
 Role-based access
 
 Cloud deployment templates (Render / Railway / Vercel)


🤝 Contributing
Pull requests are welcome!
