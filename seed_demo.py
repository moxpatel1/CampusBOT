"""
Run this ONCE after setting up the database to seed demo accounts + data.
Usage: python seed_demo.py
"""
from app import app, db, User, Assignment, Notification
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta

with app.app_context():
    db.create_all()

    demo_users = [
        {'name': 'Alex Johnson',   'email': 'student@demo.com', 'role': 'student', 'dept': 'Computer Science', 'avatar': '🎓'},
        {'name': 'Dr. Sarah Chen', 'email': 'faculty@demo.com', 'role': 'faculty', 'dept': 'Computer Science', 'avatar': '👨‍🏫'},
        {'name': 'Admin User',     'email': 'admin@demo.com',   'role': 'admin',   'dept': 'Administration',   'avatar': '🛡️'},
    ]

    for u in demo_users:
        if not User.query.filter_by(email=u['email']).first():
            user = User(
                name=u['name'], email=u['email'],
                password_hash=generate_password_hash('demo123'),
                role=u['role'], department=u['dept'], avatar=u['avatar']
            )
            db.session.add(user)
            db.session.flush()

            # Notifications
            db.session.add_all([
                Notification(user_id=user.id, title='Welcome to CampusBot 2.0!',
                             message='Your smart campus assistant is ready.', notif_type='success'),
                Notification(user_id=user.id, title='Exam schedule published',
                             message='End-semester exams: June 10–25.', notif_type='info'),
                Notification(user_id=user.id, title='Fee payment reminder',
                             message='Next payment due June 1st.', notif_type='warning'),
            ])

            # Assignments (students only)
            if u['role'] == 'student':
                db.session.add_all([
                    Assignment(title='Data Structures Assignment 3', subject='Data Structures',
                               due_date=datetime.utcnow() + timedelta(days=3), status='pending', user_id=user.id),
                    Assignment(title='OS Lab Report', subject='Operating Systems',
                               due_date=datetime.utcnow() + timedelta(days=7), status='pending', user_id=user.id),
                    Assignment(title='DBMS Mini Project', subject='Database Management',
                               due_date=datetime.utcnow() + timedelta(days=15), status='pending', user_id=user.id),
                    Assignment(title='CN Assignment 1', subject='Computer Networks',
                               due_date=datetime.utcnow() - timedelta(days=2), status='submitted', user_id=user.id, grade=88.5),
                ])

    db.session.commit()
    print("✅ Demo data seeded successfully!")
    print("   student@demo.com / demo123")
    print("   faculty@demo.com / demo123")
    print("   admin@demo.com   / demo123")
