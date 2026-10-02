# CampusBot
*Centralized University Operations & Smart Assistant*

**Project Report**
A Full-Stack Campus Management & AI Assistant Platform

**Team Members**
Bhagyesh Shah (1AUA23BCS020) | Aryan Prajapati (1AUA23BCS014) | 
Mox Patel (1AUA23BCS118) | Mulavant Nakum (1AUA23BCS119)

**Institution**
ADANI UNIVERSITY

**Guide / Supervisor**
Jayesh Solanki

**Submission Date**
April 2026

**Academic Year**
2025 – 2026

**Ahmedabad, Gujarat, India**

---

## Table of Contents
1. Introduction
2. Literature Review
3. Problem Statement & Requirements
4. Concept Development Based on Canvases
5. Implementation & Results
6. Discussion & Conclusion

---

## 1. Introduction

### 1.1 Background of the Project
Modern university environments are complex ecosystems with constantly moving parts—from evolving daily timetables and assignment deadlines to fee payments, placements, and campus events. Currently, most educational institutions rely on disjointed platforms like WhatsApp groups, physical notice boards, and clunky legacy ERP software. Students often struggle to find accurate, real-time answers to simple queries. 

CampusBot is a full-stack, comprehensive campus management platform built to solve this fragmentation. It acts as a unified portal bridging students, faculty, administration, and parents. At its core, the platform features an intelligent chatbot that answers campus-related queries instantly, alongside comprehensive modules for attendance, assignments, events, and ticket-based support.

### 1.2 Problems Explored During Ideation

**Problem 1 — College Lost and Found System**
Valuable belongings are frequently lost on campus and rarely recovered because there is no centralized digital system to report or search for them. 
*Gap identified:* Manual systems are unorganized and rely entirely on word-of-mouth.
*Reason not selected:* The concept, while useful, was too narrow in scope and did not offer enough technical complexity for a full-stack project.

**Problem 2 — Standardized University ERP Portals**
Traditional ERPs are robust but notoriously difficult for students to easily navigate on mobile devices. Data is often hidden behind too many menus.
*Gap identified:* Lack of user-friendly interfaces and absence of instant query resolution.
*Reason not selected:* Building just another ERP would not demonstrate innovation. We needed an active assistant, not just a passive database.

**Problem 3 — Centralized Campus Management & Smart Assistant (Selected)**
Students and parents lack a single, user-friendly source of truth for campus operations. Announcements get lost, fee deadlines are missed, and querying administrative staff for basic information (like library timings or curriculum details) wastes time. 
*Selection Justification:* We chose to address this by building **CampusBot**. It combines the data-management capabilities of an ERP (Placements, Fees, Timetable, Attendance, Assignments) with the conversational ease of a chatbot. This provides wide scope for complex database design and role-based access control.

### 1.3 Objectives of the Project
1. Build a robust, role-based platform allowing targeted access for Students, Faculty, Parents, and Admins.
2. Develop a Smart Chatbot capable of handling common queries (libraries, fees, hostels, exams) and falling back to FAQ database records.
3. Track and display real-time academic metrics, including assignment status, attendance thresholds, and CGPA calculations.
4. Implement a comprehensive administrative dashboard for creating events, assignments, and announcements.
5. Digitize placement drive registrations and campus-wide notifications system.

### 1.4 Scope and Limitations
CampusBot covers a wide lifecycle of student interactions on campus. The current scope includes a responsive frontend connected to a FastAPI backend and a complex PostgreSQL relational database. 
*Current limitations include:* The chat assistant relies on pre-determined conversational intent matching rather than an external Large Language Model API (to ensure data privacy and fast responses without API costs).

---

## 2. Literature Review

### 2.1 Existing Solutions and Technologies

| Platform | Strength | Gap |
|----------|----------|-----|
| Moodle / Blackboard | Excellent for course material and quizzes | Very poor for managing administrative tasks (fees, hostels), no instant chat assistant |
| WhatsApp Groups | Fast, real-time communication | Highly disorganized, important messages get buried, no structured data processing |
| Legacy University ERPs | High data security and integration | Non-intuitive UI, difficult to navigate, slow to load |

### 2.2 Gaps Identified
- Lack of a centralized intelligence (Chatbot) that can route users directly to the information they need without menu-hunting.
- Parent involvement is typically limited to end-of-semester report cards rather than active dashboard tracking.
- Absence of built-in support-ticket management for campus complaints (IT, infrastructure).

### 2.3 Justification for Our Approach
CampusBot directly addresses these gaps by creating a platform that is *proactive* rather than *reactive*. When a user is confused, they can simply type their query into the bot ("What are the library hours?"). Simultaneously, key data such as pending assignments and imminent fee dues are displayed front-and-center on dedicated dashboards.

---

## 3. Problem Statement & Requirements

### 3.1 Detailed Problem Description
Students waste significant time navigating the bureaucratic and informational architecture of university life. From finding accurate timetables to knowing exactly when a placement drive closes, the information is scattered. Furthermore, administrative staff are overburdened with repetitive queries that could be easily automated.

### 3.2 Functional Requirements

| Student View | Admin/Faculty View |
|--------------|---------------------|
| View customized daily timetables and attendance | Aggregate view of total students and staff analytics |
| Interact with CampusBot for instant answers | Create and delete campus-wide events and announcements |
| Register for Placement Drives | Mark assignments and manage due dates |
| Submit Support Tickets for complaints | Resolve and reply to support tickets |
| Calculate CGPA and view Fee status | Send targeted push-notifications to students |

### 3.3 Performance Criteria
- Stable connections to the PostgreSQL database with optimized queries for sub-second dashboard loading.
- Cryptographically secure password hashing (using `werkzeug.security`).
- Secure session management using server-side session variables.

---

## 4. Concept Development Based on Canvases

### 4.1 Empathy Mapping Canvas — Stage 1: Understand Users
**Subject:** Understanding Student and Admin experiences within the CampusBot ecosystem.
- **User Roles:** The *Student* looking to manage their academic life efficiently, and the *Admin* desiring full operational control without manual bottlenecks.
- **Activities:** Students check schedules, ask the bot for help, and submit assignments. Admins monitor overall platform health, create announcements, and handle support tickets.
- **Story Boarding (Happy Path):** A student logs in, immediately sees an upcoming assignment, talks to the Chatbot to find out how to apply for hostel leave, and effortlessly navigates to the ticket portal.

### 4.2 Ideation Canvas — Stage 2: Generate Ideas
- **Core Theme:** Unifying multiple standalone college apps into one dynamic interface.
- **Tools Identified:** Chatbot Interface, Announcements Board, Admin Analytics Dashboard, CGPA Calculator, Ticket Support Engine.
- **Why / When:** Used daily by students dynamically assessing their workload, and periodically by admins pushing crucial updates.

### 4.3 Prototype Canvas — Stage 3: Build and Test Concepts
- **Customer Promise:** "All your campus needs, one conversation away."
- **Key Features Defined:** Interactive Chat Assistant, Notification Engine, Real-time statistics (Total users, messages, pending tasks), Placement portal.
- **Customer Benefits:** Reduces anxiety for students trying to meet deadlines, saves hours of manual correspondence for administrators.

### 4.4 Product Development Canvas — Stage 4: Implementation
- **Validation:** Tested navigational ease. Evaluated if users preferred clicking through menus or asking the bot (Hybrid approach was adopted).
- **Backend Components:** Python FastAPI, PostgreSQL, SQLAlchemy.
- **Frontend Components:** Vanilla CSS Design System, HTML5 Templates, Jinja2 rendering.

---

## 5. Implementation & Results

### 5.1 Technology Stack & Architecture

| Layer | Technology | Purpose |
|-------|------------|---------|
| Database | PostgreSQL | Robust, scalable relational data storage |
| ORM | SQLAlchemy | Secure against SQL injection, object-relational mapping |
| Backend API | Python 3 + FastAPI | Core business logic, routing, auth |
| Frontend | HTML5 + CSS3 + Jinja2 | Dynamic server-side UI rendering |
| Security | Werkzeug (bcrypt) | Password hashing and security |

### 5.2 Implementation Roadmap

**Step 1 — Database Design & Migrations**
Designed a highly relational schema with over 15 tables ensuring total data normalization. Tables include `users`, `events`, `assignments`, `timetable`, `attendance`, `placement_drives`, `fee_records`, and `tickets`.

**Step 2 — Backend Routing & Auth System**
Implemented role-based decorators (`@login_required` and `@role_required`) to ensure absolute data access safety. Designed login, logout, and registration paradigms.

**Step 3 — The Chatbot Engine**
Developed an intelligent intent-matching engine prioritizing `FAQ` database searches and falling back to algorithmic keyword association (e.g., matching keywords like "library", "hostel", "fees") to provide instant context-aware replies.

**Step 4 — Admin & Utilities Dashboards**
Built the administrative backend granting CRUD capabilities. Developed student utility features including the CGPA calculator, notification polling, and placement registrations.

### 5.3 Key Features Delivered
1. **Interactive CampusBot:** A 24/7 intelligent chat module handling diverse campus queries.
2. **Role-Based Access Control:** Distinct views and permissions for Admin, Faculty, Student, and Parents.
3. **Admin Analytics:** Live dashboards displaying system-wide data blocks and user management.
4. **Academics & Utility Hub:** Built-in Timetable viewing, Assignment tracking, and CGPA Calculation.
5. **Support Ticket System:** Integrated help-desk allowing users to raise and track campus issues.

---

## 6. Discussion & Conclusion

### 6.1 Discussion

**What Worked Well**
The decision to tightly couple a Chatbot to the actual relational database was highly successful. By relying on a structured database and SQLAlchemy (FastAPI), the system successfully mitigated common data synchronization bugs found in standalone apps. The Vanilla CSS Design System provided a lightning-fast UI without the bloat of heavy front-end packages.

**Challenges Encountered**
Designing relationships for multi-faceted features such as the `placement_registrations` (which had to link specifically to `placement_drives` and `users` simultaneously) required rigorous database constraint planning. Additionally, configuring PostgreSQL authentication on modern Python 3 environments required upgrading `psycopg2` binaries.

**Comparison with Existing Solutions**
Unlike traditional university ERP systems which are rigid and unintuitive, CampusBot integrates conversational UI directly into the workflow. Unlike simple WhatsApp groups, data on CampusBot is permanent, securely attached to user profiles, and queryable.

### 6.2 Customer Benefits Achieved
- **Zero Friction Support:** Answers to common queries are instant, no waiting in lines outside administrative offices.
- **Organizational Relief:** Assignments, fees, and timetables are centralized, significantly reducing the "cognitive load" on students.
- **Admin Efficiency:** The dashboard converts raw student data into actionable metrics.

### 6.3 Future Scope
- **LLM Integration:** Upgrading the chatbot with a fine-tuned Local Large Language Model for enhanced contextual conversations.
- **WebSockets:** Upgrading instant messages and notifications to utilize real-time WebSocket streams instead of polling.
- **Payment Gateway:** Linking the Fees module to a live sandbox environment (e.g., Razorpay) to complete the online billing cycle.

### 6.4 Conclusion
CampusBot successfully achieves its vision of being a digital smart-campus. By addressing the specific pain points of fragmented university workflows, the project demonstrates how technical architectures—when intentionally designed around the user experience—can vastly improve educational administration. The platform is highly scalable, incredibly responsive, and lays a powerful foundation for future smart-campus expansions.

---
*End of Report*
