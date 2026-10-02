-- ═══════════════════════════════════════════════════════════
-- CAMPUSBOT — DATABASE SETUP
-- 1. Open pgAdmin 4
-- 2. Connect to your "PM-Chatbot" database
-- 3. Open Query Tool and run this entire file (F5)
-- ═══════════════════════════════════════════════════════════

-- ─────────────────────────────────────────
-- CLEAN SLATE
-- ─────────────────────────────────────────
DROP TABLE IF EXISTS assignments   CASCADE;
DROP TABLE IF EXISTS notifications CASCADE;
DROP TABLE IF EXISTS chat_messages CASCADE;   -- remove old table if exists
DROP TABLE IF EXISTS events        CASCADE;
DROP TABLE IF EXISTS users         CASCADE;

-- ─────────────────────────────────────────
-- USERS  (no avatar column, no fake data)
-- ─────────────────────────────────────────
CREATE TABLE users (
    id            SERIAL PRIMARY KEY,
    name          VARCHAR(100)  NOT NULL,
    email         VARCHAR(150)  UNIQUE NOT NULL,
    password_hash VARCHAR(256)  NOT NULL,
    role          VARCHAR(20)   NOT NULL DEFAULT 'student',
    department    VARCHAR(100),
    created_at    TIMESTAMP     DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- EVENTS
-- ─────────────────────────────────────────
CREATE TABLE events (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    event_type  VARCHAR(50),
    date        TIMESTAMP    NOT NULL,
    location    VARCHAR(200),
    created_by  INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    created_at  TIMESTAMP    DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- NOTIFICATIONS
-- ─────────────────────────────────────────
CREATE TABLE notifications (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER      NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    message     TEXT,
    notif_type  VARCHAR(30)  DEFAULT 'info',
    is_read     BOOLEAN      DEFAULT FALSE,
    created_at  TIMESTAMP    DEFAULT NOW()
);

-- ─────────────────────────────────────────
-- ASSIGNMENTS
-- ─────────────────────────────────────────
CREATE TABLE assignments (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    subject    VARCHAR(100),
    due_date   TIMESTAMP,
    status     VARCHAR(20)  DEFAULT 'pending',
    user_id    INTEGER      REFERENCES users(id) ON DELETE CASCADE,
    grade      FLOAT
);

-- ─────────────────────────────────────────
-- INDEXES
-- ─────────────────────────────────────────
CREATE INDEX idx_notif_user  ON notifications(user_id);
CREATE INDEX idx_assign_user ON assignments(user_id);
CREATE INDEX idx_events_date ON events(date);

-- ─────────────────────────────────────────
-- NO FAKE USERS — register through the app
-- ─────────────────────────────────────────

-- ─────────────────────────────────────────
-- VERIFY
-- ─────────────────────────────────────────
SELECT 'users'         AS table_name, COUNT(*) AS rows FROM users
UNION ALL
SELECT 'events',        COUNT(*) FROM events
UNION ALL
SELECT 'notifications', COUNT(*) FROM notifications
UNION ALL
SELECT 'assignments',   COUNT(*) FROM assignments;

-- ─────────────────────────────────────────
-- NEW TABLES (run after existing schema)
-- ─────────────────────────────────────────

DROP TABLE IF EXISTS placement_registrations CASCADE;
DROP TABLE IF EXISTS placement_drives        CASCADE;
DROP TABLE IF EXISTS user_profiles           CASCADE;
DROP TABLE IF EXISTS attendance              CASCADE;
DROP TABLE IF EXISTS timetable              CASCADE;

CREATE TABLE timetable (
    id         SERIAL PRIMARY KEY,
    department VARCHAR(100) NOT NULL,
    day        VARCHAR(10)  NOT NULL,
    time_start VARCHAR(10)  NOT NULL,
    time_end   VARCHAR(10)  NOT NULL,
    subject    VARCHAR(100) NOT NULL,
    faculty    VARCHAR(100),
    room       VARCHAR(50),
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE attendance (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    subject    VARCHAR(100) NOT NULL,
    date       DATE NOT NULL,
    status     VARCHAR(10) DEFAULT 'present',
    marked_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    UNIQUE(user_id, subject, date)
);

CREATE TABLE user_profiles (
    id       SERIAL PRIMARY KEY,
    user_id  INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    phone    VARCHAR(20),
    bio      TEXT,
    semester VARCHAR(20),
    cgpa     FLOAT,
    skills   TEXT,
    linkedin VARCHAR(200),
    github   VARCHAR(200)
);

CREATE TABLE placement_drives (
    id          SERIAL PRIMARY KEY,
    company     VARCHAR(200) NOT NULL,
    role        VARCHAR(200) NOT NULL,
    package     VARCHAR(100),
    eligibility TEXT,
    drive_date  TIMESTAMP,
    last_date   TIMESTAMP,
    description TEXT,
    status      VARCHAR(20) DEFAULT 'upcoming',
    created_by  INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at  TIMESTAMP DEFAULT NOW()
);

CREATE TABLE placement_registrations (
    id            SERIAL PRIMARY KEY,
    drive_id      INTEGER NOT NULL REFERENCES placement_drives(id) ON DELETE CASCADE,
    user_id       INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    registered_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(drive_id, user_id)
);

CREATE INDEX idx_attendance_user    ON attendance(user_id);
CREATE INDEX idx_timetable_dept     ON timetable(department);
CREATE INDEX idx_placement_status   ON placement_drives(status);

-- ─────────────────────────────────────────
-- PHASE 3 TABLES
-- ─────────────────────────────────────────
DROP TABLE IF EXISTS query_logs   CASCADE;
DROP TABLE IF EXISTS faqs         CASCADE;
DROP TABLE IF EXISTS tickets      CASCADE;
DROP TABLE IF EXISTS fee_records  CASCADE;
DROP TABLE IF EXISTS announcements CASCADE;

CREATE TABLE announcements (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    content    TEXT NOT NULL,
    priority   VARCHAR(20) DEFAULT 'normal',
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active  BOOLEAN DEFAULT TRUE
);

CREATE TABLE fee_records (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title      VARCHAR(200) NOT NULL,
    amount     FLOAT NOT NULL,
    due_date   TIMESTAMP,
    paid_date  TIMESTAMP,
    status     VARCHAR(20) DEFAULT 'pending',
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tickets (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    description TEXT,
    category    VARCHAR(50) DEFAULT 'general',
    status      VARCHAR(20) DEFAULT 'open',
    priority    VARCHAR(20) DEFAULT 'normal',
    response    TEXT,
    resolved_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at  TIMESTAMP DEFAULT NOW(),
    updated_at  TIMESTAMP DEFAULT NOW()
);public.user_profiles

CREATE TABLE faqs (
    id         SERIAL PRIMARY KEY,
    question   VARCHAR(300) NOT NULL,
    answer     TEXT NOT NULL,
    category   VARCHAR(50) DEFAULT 'general',
    created_by INTEGER REFERENCES users(id) ON DELETE SET NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE query_logs (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER REFERENCES users(id) ON DELETE SET NULL,
    query      TEXT NOT NULL,
    category   VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_fee_user    ON fee_records(user_id);
CREATE INDEX idx_ticket_user ON tickets(user_id);
CREATE INDEX idx_query_cat   ON query_logs(category);
