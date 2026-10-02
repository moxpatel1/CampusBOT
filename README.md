<div align="center">

# 🎓 CampusBot 2.0

### *Next-Generation AI-Powered Campus Assistant & ERP Portal*

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge&logo=python)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Render](https://img.shields.io/badge/Render-Deployed-46E3B7?style=for-the-badge&logo=render&logoColor=white)](https://render.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

---

CampusBot 2.0 is an intelligent, full-stack campus management and AI conversational assistant built with **FastAPI**, **SQLAlchemy**, and **Groq LLM**. It delivers personalized dashboards for Students, Faculty, Parents, and Administrators alongside real-time campus query resolution.

</div>

---

## 📌 Table of Contents
- [✨ Key Features](#-key-features)
- [🛠️ Tech Stack](#️-tech-stack)
- [📁 Directory Structure](#-directory-structure)
- [🚀 Quick Start & Installation](#-quick-start--installation)
- [🔑 Demo & Admin Credentials](#-demo--admin-credentials)
- [⚙️ Environment Configuration](#️-environment-configuration)
- [☁️ Cloud Deployment (Render)](#️-cloud-deployment-render)
- [📜 License & Contributing](#-license--contributing)

---

## ✨ Key Features

### 🤖 AI Campus Chatbot
* **Groq LLM Integration**: Fast, context-aware AI answering student & faculty queries 24/7.
* **Campus FAQ & Academic Knowledge**: Course info, syllabus details, exam schedules, and fee policies.

### 🎓 Role-Based Portals & Dashboards
* **Student Dashboard**: Attendance metrics, timetable tracker, assignment submissions, CGPA calculator, and fee receipts.
* **Faculty Portal**: Class roster, attendance logging, assignment publishing, and announcement broadcast.
* **Parent Portal**: Real-time attendance monitoring, academic progress reports, and fee payment status.
* **Admin Control Center**: User role management, campus-wide announcements, system analytics, and ticket resolution.

### ⚡ Smart Productivity Utilities
* **Ticket Management**: Support ticketing system for campus issues (IT, Library, Hostel, Transport).
* **Placement & Career Hub**: Placement announcements, company drives, and interview schedules.
* **Glassmorphic UI**: Sleek, modern interface with instant **Dark/Light Mode** toggling and responsive mobile layout.

---

## 🛠️ Tech Stack

| Domain | Technology | Description |
|---|---|---|
| **Backend** | Python 3.10+ / FastAPI | High-performance async web framework |
| **Database** | PostgreSQL / SQLite | Relational database with SQLAlchemy ORM |
| **Frontend** | HTML5, CSS3, JavaScript | Custom Design System with Dark Mode & Glassmorphism |
| **AI / LLM** | Groq API (Qwen 3.8 27B) | Ultra-fast AI conversation engine |
| **Deployment** | Render / Gunicorn / Uvicorn | Automated cloud deployment via `render.yaml` |

---

## 📁 Directory Structure

```text
CampusBOT/
├── database/
│   └── schema.sql             # SQL relational schema definitions
├── static/
│   ├── css/                   # Custom modular styling (Design system, Dark mode)
│   │   ├── admin.css
│   │   ├── dark-mode.css
│   │   ├── design-system.css
│   │   ├── features.css
│   │   └── home.css
│   └── js/
│       └── main.js            # Interactivity, AJAX, & UI controllers
├── templates/                 # Jinja2 HTML5 Templates
│   ├── admin.html
│   ├── attendance.html
│   ├── base.html
│   ├── cgpa.html
│   ├── chat.html
│   ├── dashboard.html
│   ├── index.html
│   ├── login.html
│   └── ... (20+ responsive views)
├── main.py                    # Core FastAPI backend, routing, API endpoints & ORM
├── app.py                     # Legacy application entry/wrapper
├── seed_demo.py               # Database seeder for demo users & sample records
├── run.bat                    # One-click Windows runner script
├── render.yaml                # Render Blueprint deployment manifest
├── requirements.txt           # Python dependencies manifest
├── Procfile                   # Process file for production ASGI deployment
└── .gitignore                 # Excluded environments and cache files
```

---

## 🚀 Quick Start & Installation

### Prerequisites
* **Python 3.10+** installed
* **Git** installed

### 1. Clone Repository
```bash
git clone https://github.com/moxpatel1/CampusBOT.git
cd CampusBOT
```

### 2. Create & Activate Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the root folder:
```env
DATABASE_URL=sqlite:///./campusbot.db
GROQ_API_KEY=your_groq_api_key_here
SECRET_KEY=your_secret_key_here
```

### 5. Seed Initial Data (Optional)
```bash
python seed_demo.py
```

### 6. Run Application
Double-click `run.bat` **OR** execute via terminal:
```bash
python -m uvicorn main:app --reload --port 5000
```
Visit **`http://localhost:5000`** in your browser.

---

## 🔑 Demo & Admin Credentials

| Portal Role | Email Address | Default Password |
|---|---|---|
| **🛡️ System Admin** | `admin@campusbot.com` | `Admin123!` |
| **🎓 Student** | `student@demo.com` | `demo123` |
| **👨‍🏫 Faculty** | `faculty@demo.com` | `demo123` |
| **🛡️ Secondary Admin** | `admin@demo.com` | `demo123` |

---

## ⚙️ Environment Configuration

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection string or local SQLite fallback |
| `GROQ_API_KEY` | Optional | Groq API Key for AI chatbot integration |
| `SECRET_KEY` | Yes | Secret key for JWT session encryption |
| `PORT` | Optional | Application port (Default: `5000`) |

---

## ☁️ Cloud Deployment (Render)

CampusBot includes full **Render Blueprint** support via `render.yaml`.

1. Push code to your GitHub repository.
2. Log into [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** -> Select **Blueprint**.
4. Select your **`CampusBOT`** repository.
5. Render automatically creates:
   * **PostgreSQL Database Instance**
   * **FastAPI Web Service**
6. Set your `GROQ_API_KEY` in Environment Variables and deploy!

---

## 📜 License & Contributing

Distributed under the **MIT License**. See [`LICENSE`](LICENSE) for more details.

Contributions are welcome! Please check [`CONTRIBUTING.md`](CONTRIBUTING.md) to get started.

<div align="center">
  <sub>Built with ❤️ by Mox Patel & CampusBot Team</sub>
</div>
