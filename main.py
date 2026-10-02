"""
CampusBot — FastAPI Backend
  - Starlette Sessions (itsdangerous signed cookies)
  - SQLAlchemy (same models, same DB)
  - Jinja2 templates (same templates folder)
  - All original routes preserved
"""

from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean, DateTime, Date, ForeignKey, func, text
from sqlalchemy.orm import declarative_base, sessionmaker, relationship, Session
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from groq import Groq
import os
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel

# ─────────────────────────────────────────
# SETUP
# ─────────────────────────────────────────

load_dotenv()

app = FastAPI(title="CampusBot", version="2.0")

# Session middleware (signed cookie, same as Flask secret_key)
app.add_middleware(
    SessionMiddleware,
    secret_key=os.environ.get("SECRET_KEY", "campusbot-secret-2024"),
    session_cookie="campusbot_session",
    max_age=86400 * 7,   # 7 days
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Compatibility patch for Starlette Request.url_for (handles filename='...' parameter from Flask templates)
_orig_url_for = Request.url_for
def _patched_url_for(self: Request, name: str, **path_params):
    if name == "static" and "filename" in path_params:
        path_params["path"] = path_params.pop("filename")
    return _orig_url_for(self, name, **path_params)
Request.url_for = _patched_url_for

def render_template(request: Request, name: str, context: dict = None, status_code: int = 200):
    if context is None:
        context = {}
    context["request"] = request
    context["session"] = request.session
    return templates.TemplateResponse(request=request, name=name, context=context, status_code=status_code)

# Groq AI
groq_api_key = os.environ.get("GROQ_API_KEY")
groq_client = Groq(api_key=groq_api_key) if groq_api_key else None

# In-memory chat store
chat_store: dict = {}

# ─────────────────────────────────────────
# DATABASE
# ─────────────────────────────────────────

raw_db_url = os.environ.get("DATABASE_URL", "").strip()

if not raw_db_url:
    DATABASE_URL = "sqlite:///./campusbot.db"
elif raw_db_url.startswith("postgres://"):
    DATABASE_URL = raw_db_url.replace("postgres://", "postgresql://", 1)
else:
    DATABASE_URL = raw_db_url

if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False}, pool_pre_ping=True)
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ─────────────────────────────────────────
# MODELS (identical to Flask version)
# ─────────────────────────────────────────

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True)
    name          = Column(String(100), nullable=False)
    email         = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    role          = Column(String(20), default="student")
    department    = Column(String(100))
    created_at    = Column(DateTime, default=datetime.utcnow)
    notifications = relationship("Notification", backref="user", lazy=True, foreign_keys="Notification.user_id")

class Event(Base):
    __tablename__ = "events"
    id          = Column(Integer, primary_key=True)
    title       = Column(String(200), nullable=False)
    description = Column(Text)
    event_type  = Column(String(50))
    date        = Column(DateTime, nullable=False)
    location    = Column(String(200))
    created_by  = Column(Integer, ForeignKey("users.id"))
    created_at  = Column(DateTime, default=datetime.utcnow)

class Notification(Base):
    __tablename__ = "notifications"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    title      = Column(String(200), nullable=False)
    message    = Column(Text)
    notif_type = Column(String(30), default="info")
    is_read    = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Assignment(Base):
    __tablename__ = "assignments"
    id       = Column(Integer, primary_key=True)
    title    = Column(String(200), nullable=False)
    subject  = Column(String(100))
    due_date = Column(DateTime)
    status   = Column(String(20), default="pending")
    user_id  = Column(Integer, ForeignKey("users.id"))
    grade    = Column(Float)

class TimetableEntry(Base):
    __tablename__ = "timetable"
    id         = Column(Integer, primary_key=True)
    department = Column(String(100), nullable=False)
    day        = Column(String(10), nullable=False)
    time_start = Column(String(10), nullable=False)
    time_end   = Column(String(10), nullable=False)
    subject    = Column(String(100), nullable=False)
    faculty    = Column(String(100))
    room       = Column(String(50))
    created_by = Column(Integer, ForeignKey("users.id"))

class AttendanceRecord(Base):
    __tablename__ = "attendance"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    subject    = Column(String(100), nullable=False)
    date       = Column(Date, nullable=False)
    status     = Column(String(10), default="present")
    marked_by  = Column(Integer, ForeignKey("users.id"))

class PlacementDrive(Base):
    __tablename__ = "placement_drives"
    id          = Column(Integer, primary_key=True)
    company     = Column(String(200), nullable=False)
    role        = Column(String(200), nullable=False)
    package     = Column(String(100))
    eligibility = Column(Text)
    drive_date  = Column(DateTime)
    last_date   = Column(DateTime)
    description = Column(Text)
    status      = Column(String(20), default="upcoming")
    created_by  = Column(Integer, ForeignKey("users.id"))
    created_at  = Column(DateTime, default=datetime.utcnow)

class PlacementRegistration(Base):
    __tablename__ = "placement_registrations"
    id            = Column(Integer, primary_key=True)
    drive_id      = Column(Integer, ForeignKey("placement_drives.id"), nullable=False)
    user_id       = Column(Integer, ForeignKey("users.id"), nullable=False)
    registered_at = Column(DateTime, default=datetime.utcnow)

class UserProfile(Base):
    __tablename__ = "user_profiles"
    id       = Column(Integer, primary_key=True)
    user_id  = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    phone    = Column(String(20))
    bio      = Column(Text)
    semester = Column(String(20))
    cgpa     = Column(Float)
    skills   = Column(Text)
    linkedin = Column(String(200))
    github   = Column(String(200))

class Announcement(Base):
    __tablename__ = "announcements"
    id         = Column(Integer, primary_key=True)
    title      = Column(String(200), nullable=False)
    content    = Column(Text, nullable=False)
    priority   = Column(String(20), default="normal")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active  = Column(Boolean, default=True)

class FeeRecord(Base):
    __tablename__ = "fee_records"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    title      = Column(String(200), nullable=False)
    amount     = Column(Float, nullable=False)
    due_date   = Column(DateTime)
    paid_date  = Column(DateTime)
    status     = Column(String(20), default="pending")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class Ticket(Base):
    __tablename__ = "tickets"
    id          = Column(Integer, primary_key=True)
    user_id     = Column(Integer, ForeignKey("users.id"), nullable=False)
    title       = Column(String(200), nullable=False)
    description = Column(Text)
    category    = Column(String(50), default="general")
    status      = Column(String(20), default="open")
    priority    = Column(String(20), default="normal")
    response    = Column(Text)
    resolved_by = Column(Integer, ForeignKey("users.id"))
    created_at  = Column(DateTime, default=datetime.utcnow)
    updated_at  = Column(DateTime, default=datetime.utcnow)

class FAQ(Base):
    __tablename__ = "faqs"
    id         = Column(Integer, primary_key=True)
    question   = Column(String(300), nullable=False)
    answer     = Column(Text, nullable=False)
    category   = Column(String(50), default="general")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class QueryLog(Base):
    __tablename__ = "query_logs"
    id         = Column(Integer, primary_key=True)
    user_id    = Column(Integer, ForeignKey("users.id"))
    message    = Column("query", Text, nullable=False)
    category   = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)

# ─────────────────────────────────────────
# AUTH HELPERS
# ─────────────────────────────────────────

def get_current_user_id(request: Request) -> Optional[int]:
    return request.session.get("user_id")

def require_login(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        raise HTTPException(status_code=303, headers={"Location": "/login"})
    return uid

def get_user(uid: int, db: Session) -> Optional[User]:
    return db.get(User, uid)

# ─────────────────────────────────────────
# BOT RESPONSE
# ─────────────────────────────────────────

def generate_bot_response(msg: str, uid: int, db: Session):
    # 1. Check FAQs first
    try:
        faq = db.query(FAQ).filter(FAQ.question.ilike(f"%{msg[:30]}%")).first()
        if faq:
            return faq.answer, "faq"
    except Exception:
        pass

    # 2. Groq AI
    if not groq_client:
        return "I'm currently running without a GROQ_API_KEY. Please set GROQ_API_KEY in your environment variables to enable AI responses.", "ai"

    try:
        history = chat_store.get(uid, [])
        groq_messages = [{
            "role": "system",
            "content": (
                "You are CampusBot, a helpful and friendly AI assistant for a college campus. "
                "You help students with queries about events, assignments, grades, library, fees, placements, and general campus life. "
                "Keep your responses concise, professional, and supportive. If you don't know something specific like a date or location, "
                "suggest the user check the relevant page (Events, Timetable, etc.) or contact the administration."
            )
        }]
        for turn in history[-21:-1]:
            role = "user" if turn["sender"] == "user" else "assistant"
            groq_messages.append({"role": role, "content": turn["content"]})
        groq_messages.append({"role": "user", "content": msg})

        completion = groq_client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=groq_messages,
            temperature=0.7,
            max_tokens=512,
        )
        return completion.choices[0].message.content, "ai"
    except Exception as e:
        print(f"Groq Error: {e}")
        return "I'm having trouble connecting right now. Please try again.", "error"

# ─────────────────────────────────────────
# STARTUP — create tables & seed admin
# ─────────────────────────────────────────

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin_email = "admin@campusbot.com"
        existing = db.query(User).filter_by(email=admin_email).first()
        if not existing:
            admin = User(
                name="Mox Patel", email=admin_email,
                password_hash=generate_password_hash("Admin123!"),
                role="admin", department="Administration"
            )
            db.add(admin)
            db.commit()
            print(f"[CampusBot] Admin created: {admin_email}")
        else:
            existing.name = "Mox Patel"
            existing.password_hash = generate_password_hash("Admin123!")
            existing.role = "admin"
            db.commit()
    finally:
        db.close()

# ─────────────────────────────────────────
# PAGE ROUTES
# ─────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return render_template(request, "index.html")

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/dashboard", status_code=302)
    return render_template(request, "login.html")

@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    if request.session.get("user_id"):
        return RedirectResponse("/dashboard", status_code=302)
    return render_template(request, "register.html")

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid:
        return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    if user and user.role == "parent":
        return RedirectResponse("/parent", status_code=302)
    return render_template(request, "dashboard.html", {"user": user})

@app.get("/chat", response_class=HTMLResponse)
async def chat_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid:
        return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    return render_template(request, "chat.html", {"user": user})

@app.get("/events", response_class=HTMLResponse)
async def events_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid:
        return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    return render_template(request, "events.html", {"user": user})

@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid:
        return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    if not user or user.role != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    return render_template(request, "admin.html", {"user": user})

@app.get("/parent", response_class=HTMLResponse)
async def parent_portal(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid:
        return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    if not user or user.role != "parent":
        return RedirectResponse("/dashboard", status_code=302)
    return render_template(request, "parent.html", {"user": user})

@app.get("/announcements", response_class=HTMLResponse)
async def announcements_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    return render_template(request, "announcements.html", {"user": user})

@app.get("/tickets", response_class=HTMLResponse)
async def tickets_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    return render_template(request, "tickets.html", {"user": user})

@app.get("/faq", response_class=HTMLResponse)
async def faq_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    return render_template(request, "faq.html", {"user": user})

@app.get("/cgpa", response_class=HTMLResponse)
async def cgpa_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    return render_template(request, "cgpa.html", {"user": user})

@app.get("/timetable", response_class=HTMLResponse)
async def timetable_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    return render_template(request, "timetable.html", {"user": user})

@app.get("/attendance", response_class=HTMLResponse)
async def attendance_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    return render_template(request, "attendance.html", {"user": user})

@app.get("/profile", response_class=HTMLResponse)
async def profile_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    prof = db.query(UserProfile).filter_by(user_id=uid).first()
    return render_template(request, "profile.html", {"user": user, "profile": prof})

@app.get("/placements", response_class=HTMLResponse)
async def placements_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    return render_template(request, "placements.html", {"user": user})

@app.get("/fees", response_class=HTMLResponse)
async def fees_page(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return RedirectResponse("/login", status_code=302)
    user = db.get(User, uid)
    return render_template(request, "fees.html", {"user": user})

# ─────────────────────────────────────────
# PYDANTIC SCHEMAS
# ─────────────────────────────────────────

class RegisterSchema(BaseModel):
    name: str
    email: str
    password: str
    role: str = "student"
    department: str = ""

class LoginSchema(BaseModel):
    email: str
    password: str

class ChatSchema(BaseModel):
    message: str

class EventSchema(BaseModel):
    title: str
    description: str = ""
    type: str = "academic"
    date: str
    location: str = ""

class AssignmentSchema(BaseModel):
    title: str
    subject: str = ""
    due_date: Optional[str] = None
    user_id: Optional[int] = None

class TimetableSchema(BaseModel):
    department: str
    day: str
    time_start: str
    time_end: str
    subject: str
    faculty: str = ""
    room: str = ""

class AttendanceMarkSchema(BaseModel):
    user_id: int
    subject: str
    date: str
    status: str

class ProfileSchema(BaseModel):
    name: Optional[str] = None
    department: Optional[str] = None
    phone: str = ""
    bio: str = ""
    semester: str = ""
    cgpa: Optional[float] = None
    skills: str = ""
    linkedin: str = ""
    github: str = ""

class PlacementSchema(BaseModel):
    company: str
    role: str
    package: str = ""
    eligibility: str = ""
    drive_date: Optional[str] = None
    last_date: Optional[str] = None
    description: str = ""
    status: str = "upcoming"

class AnnouncementSchema(BaseModel):
    title: str
    content: str
    priority: str = "normal"

class FeeSchema(BaseModel):
    title: str
    amount: float
    due_date: Optional[str] = None
    user_id: Optional[int] = None

class TicketSchema(BaseModel):
    title: str
    description: str = ""
    category: str = "general"
    priority: str = "normal"

class TicketRespondSchema(BaseModel):
    response: str
    status: str = "resolved"

class FAQSchema(BaseModel):
    question: str
    answer: str
    category: str = "general"

class BulkDeleteSchema(BaseModel):
    entity: str
    ids: list

class LinkStudentSchema(BaseModel):
    student_email: str

# ─────────────────────────────────────────
# AUTH API
# ─────────────────────────────────────────

@app.post("/api/auth/register")
async def api_register(data: RegisterSchema, request: Request, db: Session = Depends(get_db)):
    if not data.name or not data.email or not data.password:
        return JSONResponse({"error": "All fields are required"}, status_code=400)
    if len(data.password) < 6:
        return JSONResponse({"error": "Password must be at least 6 characters"}, status_code=400)
    if db.query(User).filter_by(email=data.email.lower().strip()).first():
        return JSONResponse({"error": "This email is already registered"}, status_code=400)
    user = User(
        name=data.name.strip(),
        email=data.email.lower().strip(),
        password_hash=generate_password_hash(data.password),
        role=data.role,
        department=data.department
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    request.session["user_id"]   = user.id
    request.session["user_name"] = user.name
    request.session["user_role"] = user.role
    return {"success": True, "redirect": "/dashboard"}

@app.post("/api/auth/login")
async def api_login(data: LoginSchema, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter_by(email=data.email.lower().strip()).first()
    if not user or not check_password_hash(user.password_hash, data.password):
        return JSONResponse({"error": "Invalid email or password"}, status_code=401)
    request.session["user_id"]   = user.id
    request.session["user_name"] = user.name
    request.session["user_role"] = user.role
    return {"success": True, "redirect": "/dashboard"}

@app.post("/api/auth/logout")
async def api_logout(request: Request):
    uid = request.session.get("user_id")
    if uid and uid in chat_store:
        del chat_store[uid]
    request.session.clear()
    return {"success": True}

# ─────────────────────────────────────────
# CHAT API
# ─────────────────────────────────────────

@app.post("/api/chat")
async def api_chat(data: ChatSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    msg = data.message.strip()
    if not msg:
        return JSONResponse({"error": "Empty message"}, status_code=400)
    now = datetime.utcnow().strftime("%I:%M %p")
    if uid not in chat_store:
        chat_store[uid] = []
    chat_store[uid].append({"sender": "user", "content": msg, "timestamp": now})
    bot_reply, category = generate_bot_response(msg, uid, db)
    chat_store[uid].append({"sender": "bot", "content": bot_reply, "timestamp": now})
    db.add(QueryLog(user_id=uid, message=msg, category=category))
    db.commit()
    if len(chat_store[uid]) > 100:
        chat_store[uid] = chat_store[uid][-100:]
    return {"reply": bot_reply, "timestamp": now}

@app.get("/api/chat/history")
async def api_chat_history(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return chat_store.get(uid, [])

@app.post("/api/chat/clear")
async def api_chat_clear(request: Request):
    uid = request.session.get("user_id")
    if not uid:
        return JSONResponse({"error": "Unauthorized"}, status_code=401)
    chat_store[uid] = []
    return {"success": True}

# ─────────────────────────────────────────
# NOTIFICATIONS API
# ─────────────────────────────────────────

@app.get("/api/notifications")
async def api_notifications(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    notifs = db.query(Notification).filter_by(user_id=uid)\
        .order_by(Notification.created_at.desc()).limit(20).all()
    return [{"id": n.id, "title": n.title, "message": n.message,
             "type": n.notif_type, "is_read": n.is_read,
             "created_at": n.created_at.strftime("%b %d, %I:%M %p")} for n in notifs]

@app.post("/api/notifications/read")
async def api_mark_read(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    db.query(Notification).filter_by(user_id=uid, is_read=False).update({"is_read": True})
    db.commit()
    return {"success": True}

# ─────────────────────────────────────────
# EVENTS API
# ─────────────────────────────────────────

@app.get("/api/events")
async def api_events(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    evts = db.query(Event).order_by(Event.date.asc()).all()
    return [{"id": e.id, "title": e.title, "description": e.description,
             "type": e.event_type, "date": e.date.strftime("%b %d, %Y  %I:%M %p"),
             "location": e.location} for e in evts]

@app.post("/api/events")
async def api_create_event(data: EventSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Only admin or faculty can create events"}, status_code=403)
    try:
        event = Event(title=data.title.strip(), description=data.description.strip(),
                      event_type=data.type, date=datetime.fromisoformat(data.date),
                      location=data.location.strip(), created_by=uid)
        db.add(event)
        for u in db.query(User).all():
            db.add(Notification(user_id=u.id, title=f"New Event: {event.title}",
                                message=f"{event.event_type.title()} event on {event.date.strftime('%b %d, %Y')}" +
                                        (f" at {event.location}" if event.location else ""),
                                notif_type="info"))
        db.commit()
        return {"success": True, "id": event.id}
    except Exception as ex:
        db.rollback()
        return JSONResponse({"error": str(ex)}, status_code=500)

@app.delete("/api/events/{eid}")
async def api_delete_event(eid: int, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    e = db.get(Event, eid)
    if not e: raise HTTPException(status_code=404)
    db.delete(e); db.commit()
    return {"success": True}

# ─────────────────────────────────────────
# ASSIGNMENTS API
# ─────────────────────────────────────────

@app.get("/api/assignments")
async def api_assignments(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    rows = db.query(Assignment).filter_by(user_id=uid).order_by(Assignment.due_date.asc()).all()
    return [{"id": a.id, "title": a.title, "subject": a.subject,
             "due_date": a.due_date.strftime("%b %d, %Y") if a.due_date else None,
             "status": a.status, "grade": a.grade} for a in rows]

@app.post("/api/admin/assignments")
async def api_admin_create_assignment(data: AssignmentSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    due_dt = datetime.fromisoformat(data.due_date) if data.due_date else None
    users_to_assign = [db.get(User, int(data.user_id))] if data.user_id else db.query(User).filter_by(role="student").all()
    if not users_to_assign:
        return JSONResponse({"error": "No students found"}, status_code=400)
    try:
        created = 0
        for u in users_to_assign:
            if not u: continue
            db.add(Assignment(title=data.title.strip(), subject=data.subject.strip(),
                              due_date=due_dt, status="pending", user_id=u.id))
            db.add(Notification(user_id=u.id, title=f"New Assignment: {data.title}",
                                message=f"Subject: {data.subject}" + (f" | Due: {due_dt.strftime('%b %d, %Y')}" if due_dt else ""),
                                notif_type="warning"))
            created += 1
        db.commit()
        return {"success": True, "created": created}
    except Exception as ex:
        db.rollback()
        return JSONResponse({"error": str(ex)}, status_code=500)

@app.get("/api/admin/assignments")
async def api_admin_get_assignments(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    rows = db.query(Assignment).order_by(Assignment.due_date.asc()).all()
    result = []
    for a in rows:
        au = db.get(User, a.user_id) if a.user_id else None
        result.append({"id": a.id, "title": a.title, "subject": a.subject,
                       "due_date": a.due_date.strftime("%b %d, %Y") if a.due_date else None,
                       "status": a.status, "user_id": a.user_id,
                       "user_name": au.name if au else "—"})
    return result

@app.delete("/api/admin/assignments/{aid}")
async def api_admin_delete_assignment(aid: int, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    a = db.get(Assignment, aid)
    if not a: raise HTTPException(status_code=404)
    db.delete(a); db.commit()
    return {"success": True}

# ─────────────────────────────────────────
# STATS API
# ─────────────────────────────────────────

@app.get("/api/stats")
async def api_stats(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    return {
        "total_messages": len(chat_store.get(uid, [])),
        "pending_assignments": db.query(Assignment).filter_by(user_id=uid, status="pending").count(),
        "unread_notifications": db.query(Notification).filter_by(user_id=uid, is_read=False).count(),
        "upcoming_events": db.query(Event).filter(Event.date >= datetime.utcnow()).count()
    }

# ─────────────────────────────────────────
# ADMIN API
# ─────────────────────────────────────────

@app.get("/api/admin/stats")
async def api_admin_stats(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    return {
        "total_users": db.query(User).count(),
        "total_students": db.query(User).filter_by(role="student").count(),
        "total_faculty": db.query(User).filter_by(role="faculty").count(),
        "total_messages": sum(len(v) for v in chat_store.values()),
        "total_events": db.query(Event).count(),
        "total_assignments": db.query(Assignment).count(),
    }

@app.get("/api/admin/users")
async def api_admin_users(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [{"id": u.id, "name": u.name, "email": u.email, "role": u.role,
             "department": u.department, "created_at": u.created_at.strftime("%b %d, %Y")} for u in users]

@app.delete("/api/admin/users/{target_uid}")
async def api_delete_user(target_uid: int, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    if target_uid == uid:
        return JSONResponse({"error": "Cannot delete yourself"}, status_code=400)
    target = db.get(User, target_uid)
    if not target: raise HTTPException(status_code=404)
    db.query(Assignment).filter_by(user_id=target_uid).delete()
    db.query(Notification).filter_by(user_id=target_uid).delete()
    db.delete(target); db.commit()
    if target_uid in chat_store: del chat_store[target_uid]
    return {"success": True}

@app.post("/api/admin/bulk-delete")
async def api_bulk_delete(data: BulkDeleteSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    deleted = 0
    if data.entity == "users":
        for tid in data.ids:
            if tid == uid: continue
            t = db.get(User, tid)
            if t:
                db.query(Assignment).filter_by(user_id=tid).delete()
                db.query(Notification).filter_by(user_id=tid).delete()
                db.delete(t)
                if tid in chat_store: del chat_store[tid]
                deleted += 1
    elif data.entity == "events":
        for eid in data.ids:
            ev = db.get(Event, eid)
            if ev: db.delete(ev); deleted += 1
    elif data.entity == "assignments":
        for aid in data.ids:
            a = db.get(Assignment, aid)
            if a: db.delete(a); deleted += 1
    else:
        return JSONResponse({"error": "Unknown entity"}, status_code=400)
    db.commit()
    return {"success": True, "deleted": deleted}

# ─────────────────────────────────────────
# TIMETABLE API
# ─────────────────────────────────────────

@app.get("/api/timetable")
async def api_get_timetable(request: Request, department: str = "", db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    dept = department or (user.department or "")
    entries = db.query(TimetableEntry).filter_by(department=dept)\
        .order_by(TimetableEntry.day, TimetableEntry.time_start).all()
    return [{"id": e.id, "day": e.day, "time_start": e.time_start, "time_end": e.time_end,
             "subject": e.subject, "faculty": e.faculty, "room": e.room, "department": e.department} for e in entries]

@app.post("/api/timetable")
async def api_create_timetable(data: TimetableSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    try:
        entry = TimetableEntry(department=data.department, day=data.day,
                               time_start=data.time_start, time_end=data.time_end,
                               subject=data.subject, faculty=data.faculty, room=data.room, created_by=uid)
        db.add(entry); db.commit(); db.refresh(entry)
        return {"success": True, "id": entry.id}
    except Exception as ex:
        db.rollback()
        return JSONResponse({"error": str(ex)}, status_code=500)

@app.delete("/api/timetable/{eid}")
async def api_delete_timetable(eid: int, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    e = db.get(TimetableEntry, eid)
    if not e: raise HTTPException(status_code=404)
    db.delete(e); db.commit()
    return {"success": True}

# ─────────────────────────────────────────
# ATTENDANCE API
# ─────────────────────────────────────────

@app.get("/api/attendance")
async def api_get_attendance(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    records = db.query(AttendanceRecord).filter_by(user_id=uid)\
        .order_by(AttendanceRecord.date.desc()).all()
    subjects = {}
    for r in records:
        if r.subject not in subjects:
            subjects[r.subject] = {"present": 0, "absent": 0, "records": []}
        subjects[r.subject][r.status] += 1
        subjects[r.subject]["records"].append({"date": r.date.strftime("%b %d, %Y"), "status": r.status})
    result = []
    for subj, d in subjects.items():
        total = d["present"] + d["absent"]
        result.append({"subject": subj, "present": d["present"], "absent": d["absent"],
                       "total": total, "percentage": round((d["present"] / total) * 100) if total else 0,
                       "records": d["records"][:10]})
    return result

@app.post("/api/attendance/mark-one")
async def api_mark_one_attendance(data: AttendanceMarkSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    try:
        date_obj = datetime.strptime(data.date, "%Y-%m-%d").date()
        existing = db.query(AttendanceRecord).filter_by(
            user_id=data.user_id, subject=data.subject, date=date_obj).first()
        if existing:
            existing.status = data.status
        else:
            db.add(AttendanceRecord(user_id=data.user_id, subject=data.subject,
                                    date=date_obj, status=data.status, marked_by=uid))
        db.commit()
        return {"success": True}
    except Exception as ex:
        db.rollback()
        return JSONResponse({"error": str(ex)}, status_code=500)

@app.get("/api/admin/attendance-day")
async def api_admin_attendance_day(request: Request, subject: str = "", date: str = "",
                                    department: str = "", db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        query = db.query(AttendanceRecord).filter_by(subject=subject, date=date_obj)
        if department:
            student_ids = [u.id for u in db.query(User).filter_by(role="student", department=department).all()]
            query = query.filter(AttendanceRecord.user_id.in_(student_ids))
        records = query.all()
        return [{"user_id": r.user_id, "status": r.status} for r in records]
    except Exception:
        return []

# ─────────────────────────────────────────
# PROFILE API
# ─────────────────────────────────────────

@app.get("/api/profile")
async def api_get_profile(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    prof = db.query(UserProfile).filter_by(user_id=uid).first()
    return {"name": user.name, "email": user.email, "role": user.role,
            "department": user.department, "created_at": user.created_at.strftime("%b %d, %Y"),
            "phone": prof.phone if prof else "", "bio": prof.bio if prof else "",
            "semester": prof.semester if prof else "", "cgpa": prof.cgpa if prof else "",
            "skills": prof.skills if prof else "", "linkedin": prof.linkedin if prof else "",
            "github": prof.github if prof else ""}

@app.post("/api/profile")
async def api_update_profile(data: ProfileSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    try:
        if data.name: user.name = data.name.strip(); request.session["user_name"] = user.name
        if data.department: user.department = data.department.strip()
        prof = db.query(UserProfile).filter_by(user_id=uid).first()
        if not prof:
            prof = UserProfile(user_id=uid); db.add(prof)
        prof.phone = data.phone; prof.bio = data.bio; prof.semester = data.semester
        prof.cgpa = data.cgpa; prof.skills = data.skills
        prof.linkedin = data.linkedin; prof.github = data.github
        db.commit()
        return {"success": True}
    except Exception as ex:
        db.rollback()
        return JSONResponse({"error": str(ex)}, status_code=500)

# ─────────────────────────────────────────
# PLACEMENTS API
# ─────────────────────────────────────────

@app.get("/api/placements")
async def api_get_placements(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    drives = db.query(PlacementDrive).order_by(PlacementDrive.drive_date.asc()).all()
    registered_ids = {r.drive_id for r in db.query(PlacementRegistration).filter_by(user_id=uid).all()}
    return [{"id": d.id, "company": d.company, "role": d.role, "package": d.package,
             "eligibility": d.eligibility,
             "drive_date": d.drive_date.strftime("%b %d, %Y") if d.drive_date else None,
             "last_date": d.last_date.strftime("%b %d, %Y") if d.last_date else None,
             "description": d.description, "status": d.status,
             "registered": d.id in registered_ids} for d in drives]

@app.post("/api/placements")
async def api_create_placement(data: PlacementSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    try:
        drive = PlacementDrive(company=data.company.strip(), role=data.role.strip(),
                               package=data.package, eligibility=data.eligibility,
                               drive_date=datetime.fromisoformat(data.drive_date) if data.drive_date else None,
                               last_date=datetime.fromisoformat(data.last_date) if data.last_date else None,
                               description=data.description, status=data.status, created_by=uid)
        db.add(drive)
        for s in db.query(User).filter_by(role="student").all():
            db.add(Notification(user_id=s.id, title=f"Placement Drive: {drive.company}",
                                message=f"{drive.role} | {drive.package or 'Package TBD'}", notif_type="info"))
        db.commit(); db.refresh(drive)
        return {"success": True, "id": drive.id}
    except Exception as ex:
        db.rollback()
        return JSONResponse({"error": str(ex)}, status_code=500)

@app.post("/api/placements/{did}/register")
async def api_register_placement(did: int, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    if db.query(PlacementRegistration).filter_by(drive_id=did, user_id=uid).first():
        return JSONResponse({"error": "Already registered"}, status_code=400)
    db.add(PlacementRegistration(drive_id=did, user_id=uid)); db.commit()
    return {"success": True}

@app.delete("/api/placements/{did}")
async def api_delete_placement(did: int, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    d = db.get(PlacementDrive, did)
    if not d: raise HTTPException(status_code=404)
    db.query(PlacementRegistration).filter_by(drive_id=did).delete()
    db.delete(d); db.commit()
    return {"success": True}

# ─────────────────────────────────────────
# ANNOUNCEMENTS API
# ─────────────────────────────────────────

@app.get("/api/announcements")
async def api_get_announcements(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    items = db.query(Announcement).filter_by(is_active=True)\
        .order_by(Announcement.created_at.desc()).all()
    return [{"id": a.id, "title": a.title, "content": a.content,
             "priority": a.priority, "created_at": a.created_at.strftime("%b %d, %Y %I:%M %p")} for a in items]

@app.post("/api/announcements")
async def api_create_announcement(data: AnnouncementSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    ann = Announcement(title=data.title.strip(), content=data.content.strip(),
                       priority=data.priority, created_by=uid)
    db.add(ann)
    for u in db.query(User).all():
        db.add(Notification(user_id=u.id, title=f"Announcement: {ann.title}",
                            message=ann.content[:100],
                            notif_type="info" if data.priority == "normal" else "warning"))
    db.commit(); db.refresh(ann)
    return {"success": True, "id": ann.id}

@app.delete("/api/announcements/{aid}")
async def api_delete_announcement(aid: int, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    a = db.get(Announcement, aid)
    if not a: raise HTTPException(status_code=404)
    db.delete(a); db.commit()
    return {"success": True}

# ─────────────────────────────────────────
# FEES API
# ─────────────────────────────────────────

@app.get("/api/fees")
async def api_get_fees(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    records = db.query(FeeRecord).filter_by(user_id=uid).order_by(FeeRecord.due_date.asc()).all()
    return [{"id": r.id, "title": r.title, "amount": r.amount,
             "due_date": r.due_date.strftime("%b %d, %Y") if r.due_date else None,
             "paid_date": r.paid_date.strftime("%b %d, %Y") if r.paid_date else None,
             "status": r.status} for r in records]

@app.post("/api/fees/{fid}/pay")
async def api_pay_fee(fid: int, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    record = db.get(FeeRecord, fid)
    if not record: raise HTTPException(status_code=404)
    if record.user_id != uid: return JSONResponse({"error": "Unauthorized"}, status_code=403)
    record.status = "paid"; record.paid_date = datetime.utcnow()
    db.commit()
    return {"success": True}

@app.post("/api/admin/fees")
async def api_admin_create_fee(data: FeeSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    students = [db.get(User, int(data.user_id))] if data.user_id else db.query(User).filter_by(role="student").all()
    count = 0
    for s in students:
        if not s: continue
        db.add(FeeRecord(user_id=s.id, title=data.title.strip(), amount=data.amount,
                         due_date=datetime.fromisoformat(data.due_date) if data.due_date else None,
                         created_by=uid))
        db.add(Notification(user_id=s.id, title=f"Fee Due: {data.title}",
                            message=f"Amount: ₹{data.amount}", notif_type="warning"))
        count += 1
    db.commit()
    return {"success": True, "created": count}

@app.get("/api/admin/fees")
async def api_admin_get_fees(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    records = db.query(FeeRecord).order_by(FeeRecord.created_at.desc()).all()
    return [{"id": r.id, "title": r.title, "amount": r.amount, "status": r.status,
             "due_date": r.due_date.strftime("%b %d, %Y") if r.due_date else None,
             "user_name": db.get(User, r.user_id).name if db.get(User, r.user_id) else "—"} for r in records]

# ─────────────────────────────────────────
# TICKETS API
# ─────────────────────────────────────────

@app.get("/api/tickets")
async def api_get_tickets(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    tickets = db.query(Ticket).order_by(Ticket.created_at.desc()).all() if user.role in ("admin", "faculty") \
        else db.query(Ticket).filter_by(user_id=uid).order_by(Ticket.created_at.desc()).all()
    return [{"id": t.id, "title": t.title, "description": t.description,
             "category": t.category, "status": t.status, "priority": t.priority,
             "response": t.response, "created_at": t.created_at.strftime("%b %d, %Y"),
             "user_name": db.get(User, t.user_id).name if db.get(User, t.user_id) else "—"} for t in tickets]

@app.post("/api/tickets")
async def api_create_ticket(data: TicketSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    t = Ticket(user_id=uid, title=data.title.strip(), description=data.description.strip(),
               category=data.category, priority=data.priority)
    db.add(t); db.commit(); db.refresh(t)
    return {"success": True, "id": t.id}

@app.post("/api/tickets/{tid}/respond")
async def api_respond_ticket(tid: int, data: TicketRespondSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    t = db.get(Ticket, tid)
    if not t: raise HTTPException(status_code=404)
    t.response = data.response; t.status = data.status
    t.resolved_by = uid; t.updated_at = datetime.utcnow()
    db.add(Notification(user_id=t.user_id, title=f"Ticket #{t.id} Updated",
                        message=f"Status: {t.status} — {t.response[:80]}", notif_type="success"))
    db.commit()
    return {"success": True}

# ─────────────────────────────────────────
# FAQ API
# ─────────────────────────────────────────

@app.get("/api/faqs")
async def api_get_faqs(request: Request, q: str = "", db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    faqs = db.query(FAQ).order_by(FAQ.created_at.desc()).all()
    if q:
        faqs = [f for f in faqs if q.lower() in f.question.lower() or q.lower() in f.answer.lower()]
    return [{"id": f.id, "question": f.question, "answer": f.answer, "category": f.category} for f in faqs]

@app.post("/api/faqs")
async def api_create_faq(data: FAQSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    f = FAQ(question=data.question.strip(), answer=data.answer.strip(),
            category=data.category, created_by=uid)
    db.add(f); db.commit(); db.refresh(f)
    return {"success": True, "id": f.id}

@app.delete("/api/faqs/{fid}")
async def api_delete_faq(fid: int, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role not in ("admin", "faculty"):
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    f = db.get(FAQ, fid)
    if not f: raise HTTPException(status_code=404)
    db.delete(f); db.commit()
    return {"success": True}

# ─────────────────────────────────────────
# QUERY ANALYTICS API
# ─────────────────────────────────────────

@app.get("/api/admin/query-analytics")
async def api_query_analytics(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role != "admin":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    try:
        top = db.execute(text("SELECT category, COUNT(*) as cnt FROM query_logs GROUP BY category ORDER BY cnt DESC LIMIT 10")).fetchall()
        recent = db.execute(text("SELECT query, category, created_at FROM query_logs ORDER BY created_at DESC LIMIT 20")).fetchall()
        total = db.execute(text("SELECT COUNT(*) FROM query_logs")).scalar()
        return {"total": total or 0,
                "by_category": [{"category": r[0] or "other", "count": r[1]} for r in top],
                "recent": [{"query": r[0], "category": r[1],
                            "created_at": r[2].strftime("%b %d, %I:%M %p") if r[2] else ""} for r in recent]}
    except Exception as ex:
        return {"total": 0, "by_category": [], "recent": [], "error": str(ex)}

# ─────────────────────────────────────────
# PARENT API
# ─────────────────────────────────────────

@app.post("/api/parent/link-student")
async def api_parent_link_student(data: LinkStudentSchema, request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role != "parent":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    student = db.query(User).filter_by(email=data.student_email.lower().strip(), role="student").first()
    if not student:
        return JSONResponse({"error": "No student found with that email"}, status_code=404)
    prof = db.query(UserProfile).filter_by(user_id=uid).first()
    if not prof:
        prof = UserProfile(user_id=uid); db.add(prof)
    prof.bio = str(student.id); db.commit()
    return {"success": True, "student_name": student.name, "student_id": student.id}

@app.get("/api/parent/student-data")
async def api_parent_student_data(request: Request, db: Session = Depends(get_db)):
    uid = request.session.get("user_id")
    if not uid: return JSONResponse({"error": "Unauthorized"}, status_code=401)
    user = db.get(User, uid)
    if not user or user.role != "parent":
        return JSONResponse({"error": "Unauthorized"}, status_code=403)
    prof = db.query(UserProfile).filter_by(user_id=uid).first()
    if not prof or not prof.bio or not prof.bio.isdigit():
        return {"linked": False, "message": "No student linked yet"}
    student = db.get(User, int(prof.bio))
    if not student:
        return {"linked": False, "message": "Linked student not found"}
    sid = student.id
    assignments = db.query(Assignment).filter_by(user_id=sid).order_by(Assignment.due_date.asc()).all()
    att_records = db.query(AttendanceRecord).filter_by(user_id=sid).all()
    fees = db.query(FeeRecord).filter_by(user_id=sid).all()
    notifs = db.query(Notification).filter_by(user_id=sid).order_by(Notification.created_at.desc()).limit(5).all()
    subjects = {}
    for rec in att_records:
        if rec.subject not in subjects:
            subjects[rec.subject] = {"present": 0, "absent": 0}
        subjects[rec.subject][rec.status] += 1
    att_summary = [{"subject": s, "present": d["present"], "absent": d["absent"],
                    "total": d["present"] + d["absent"],
                    "percentage": round((d["present"] / (d["present"] + d["absent"])) * 100) if (d["present"] + d["absent"]) else 0}
                   for s, d in subjects.items()]
    return {"linked": True,
            "student": {"id": student.id, "name": student.name, "email": student.email, "department": student.department or "—"},
            "assignments": [{"title": a.title, "subject": a.subject,
                             "due_date": a.due_date.strftime("%b %d, %Y") if a.due_date else None,
                             "status": a.status} for a in assignments],
            "attendance": att_summary,
            "fees": [{"title": f.title, "amount": f.amount, "status": f.status,
                      "due_date": f.due_date.strftime("%b %d, %Y") if f.due_date else None} for f in fees],
            "notifications": [{"title": n.title, "message": n.message,
                               "created_at": n.created_at.strftime("%b %d")} for n in notifs],
            "upcoming_events": db.query(Event).filter(Event.date >= datetime.utcnow()).count()}
