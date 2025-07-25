#!/usr/bin/env python3
"""
EduCareer+ Database Initialization Script
Creates all necessary database tables
"""

import sqlite3
import os

def init_database():
    """Initialize the EduCareer+ database with all required tables"""
    
    print("🔧 Initializing EduCareer+ database...")
    
    # Remove existing database if it exists
    if os.path.exists('educareer_plus.db'):
        os.remove('educareer_plus.db')
        print("🗑️ Removed existing database")
    
    conn = sqlite3.connect('educareer_plus.db')
    cursor = conn.cursor()
    
    print("📋 Creating database tables...")
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            user_type TEXT NOT NULL,
            profile_data TEXT,
            created_at TIMESTAMP,
            is_verified BOOLEAN DEFAULT FALSE
        )
    ''')
    print("✅ Created users table")
    
    # Jobs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            employer_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            requirements TEXT,
            location TEXT NOT NULL,
            salary_range TEXT,
            job_type TEXT NOT NULL,
            category TEXT NOT NULL,
            skills_required TEXT,
            is_verified BOOLEAN DEFAULT FALSE,
            posted_date TIMESTAMP,
            expires_date TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            FOREIGN KEY (employer_id) REFERENCES users (id)
        )
    ''')
    print("✅ Created jobs table")
    
    # Applications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id TEXT PRIMARY KEY,
            job_id TEXT NOT NULL,
            applicant_id TEXT NOT NULL,
            status TEXT DEFAULT 'applied',
            applied_date TIMESTAMP,
            cover_letter TEXT,
            resume_path TEXT,
            video_intro_path TEXT,
            FOREIGN KEY (job_id) REFERENCES jobs (id),
            FOREIGN KEY (applicant_id) REFERENCES users (id)
        )
    ''')
    print("✅ Created applications table")
    
    # Messages table for real-time communication
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY,
            sender_id TEXT NOT NULL,
            receiver_id TEXT NOT NULL,
            job_id TEXT,
            message TEXT NOT NULL,
            timestamp TIMESTAMP,
            is_read BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (sender_id) REFERENCES users (id),
            FOREIGN KEY (receiver_id) REFERENCES users (id)
        )
    ''')
    print("✅ Created messages table")
    
    # Skill assessments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skill_assessments (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            skill_name TEXT NOT NULL,
            score INTEGER,
            assessment_date TIMESTAMP,
            certificate_path TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    print("✅ Created skill_assessments table")
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_employer ON jobs(employer_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_jobs_active ON jobs(is_active)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_applications_applicant ON applications(applicant_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_sender ON messages(sender_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_messages_receiver ON messages(receiver_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_assessments_user ON skill_assessments(user_id)')
    
    print("✅ Created database indexes")
    
    conn.commit()
    conn.close()
    
    print("🎉 Database initialization completed successfully!")
    print(f"📁 Database file: {os.path.abspath('educareer_plus.db')}")

if __name__ == "__main__":
    init_database()