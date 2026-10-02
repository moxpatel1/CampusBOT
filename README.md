# CampusBot 2.0 🤖

A next-generation AI-powered college assistant platform.

## Stack
- **Frontend**: HTML5 + CSS3 + Vanilla JS (Glassmorphism UI, Light/Dark Modes)
- **Backend**: Python FastAPI (Uvicorn ASGI Server)
- **Database**: PostgreSQL (SQLAlchemy ORM)
- **AI**: Groq API (Qwen 3.8 27B model)

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Set up PostgreSQL
Create a database named `PM-Chatbot` or set your `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql+psycopg2://user:password@localhost:5432/PM-Chatbot
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
```

### 3. Seed demo data
```bash
python seed_demo.py
```

### 4. Run the app locally
Double click `run.bat` OR run via terminal:
```bash
python -m uvicorn main:app --reload --port 5000
```

Visit `http://localhost:5000`

## Live Deployment on Render 🚀

1. Push this repository to **GitHub**.
2. Go to [Render Dashboard](https://dashboard.render.com/) -> Click **New +** -> Select **Blueprint**.
3. Connect your repository — Render will automatically detect `render.yaml` and set up the **FastAPI Web Service** and **PostgreSQL Database**.
4. Add your `GROQ_API_KEY` under Environment Variables in Render.
5. Click **Deploy**!

## Admin Account
| Role  | Email                     | Password     |
|-------|---------------------------|--------------|
| Admin | admin@campusbot.com | Admin123! |

## Features
- 🤖 AI Campus Chatbot
- 📊 Personalized Dashboards
- 🔔 Real-time Notifications
- 📅 Event & Academic Tracking
- 🎓 Role-Based Portals (Student / Faculty / Admin)
- 📈 Data-Driven Insights
