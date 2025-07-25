import sqlite3
import hashlib
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

class JobPortalDB:
    def __init__(self, db_name="educareer_plus.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_name)
    
    def init_database(self):
        """Initialize all database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table (Job Seekers)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT,
                user_type TEXT DEFAULT 'job_seeker',
                profile_complete BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_verified BOOLEAN DEFAULT FALSE,
                profile_image TEXT
            )
        ''')
        
        # User Profiles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                bio TEXT,
                location TEXT,
                experience_years INTEGER,
                current_position TEXT,
                education_level TEXT,
                skills TEXT, -- JSON array
                languages TEXT, -- JSON array
                portfolio_url TEXT,
                linkedin_url TEXT,
                github_url TEXT,
                video_resume_url TEXT,
                resume_url TEXT,
                availability TEXT,
                salary_expectation TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Employers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                company_name TEXT NOT NULL,
                company_type TEXT, -- school, college, company, ngo
                contact_person TEXT,
                phone TEXT,
                address TEXT,
                website TEXT,
                description TEXT,
                employee_count TEXT,
                industry TEXT,
                is_verified BOOLEAN DEFAULT FALSE,
                verification_documents TEXT, -- JSON array
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                logo_url TEXT,
                naac_grade TEXT,
                nba_accredited BOOLEAN DEFAULT FALSE
            )
        ''')
        
        # Jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employer_id INTEGER,
                title TEXT NOT NULL,
                description TEXT NOT NULL,
                requirements TEXT,
                location TEXT,
                job_type TEXT, -- full-time, part-time, contract, internship
                experience_level TEXT, -- fresher, 1-3, 3-5, 5+
                salary_range TEXT,
                skills_required TEXT, -- JSON array
                benefits TEXT,
                application_deadline DATE,
                is_active BOOLEAN DEFAULT TRUE,
                is_verified BOOLEAN DEFAULT TRUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                view_count INTEGER DEFAULT 0,
                application_count INTEGER DEFAULT 0,
                category TEXT, -- teaching, admin, technical, etc.
                is_premium BOOLEAN DEFAULT FALSE,
                auto_expire_date DATE
            )
        ''')
        
        # Job Applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_id INTEGER,
                user_id INTEGER,
                cover_letter TEXT,
                status TEXT DEFAULT 'applied', -- applied, shortlisted, interviewed, hired, rejected
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                employer_notes TEXT,
                interview_scheduled TIMESTAMP,
                FOREIGN KEY (job_id) REFERENCES jobs (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Skill Assessments table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS skill_assessments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                skill_name TEXT,
                assessment_type TEXT, -- coding, communication, domain_specific
                score INTEGER,
                max_score INTEGER,
                certificate_url TEXT,
                completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Messages table for real-time communication
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER,
                receiver_id INTEGER,
                sender_type TEXT, -- user, employer
                receiver_type TEXT, -- user, employer
                message TEXT,
                is_read BOOLEAN DEFAULT FALSE,
                sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                application_id INTEGER,
                FOREIGN KEY (application_id) REFERENCES applications (id)
            )
        ''')
        
        # Institutions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS institutions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT, -- college, school, university
                address TEXT,
                contact_email TEXT,
                contact_phone TEXT,
                principal_name TEXT,
                affiliation TEXT,
                naac_grade TEXT,
                established_year INTEGER,
                student_count INTEGER,
                is_verified BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Student Placements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS student_placements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                institution_id INTEGER,
                student_name TEXT,
                student_email TEXT,
                course TEXT,
                graduation_year INTEGER,
                cgpa REAL,
                skills TEXT, -- JSON array
                placement_status TEXT DEFAULT 'seeking', -- seeking, placed, not_interested
                placed_company TEXT,
                package_offered TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (institution_id) REFERENCES institutions (id)
            )
        ''')
        
        # Job Recommendations table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS job_recommendations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                job_id INTEGER,
                match_score REAL,
                reasons TEXT, -- JSON array of matching reasons
                is_viewed BOOLEAN DEFAULT FALSE,
                recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (job_id) REFERENCES jobs (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def create_user(self, email: str, password: str, full_name: str, phone: str = None, user_type: str = 'job_seeker') -> bool:
        """Create a new user"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO users (email, password_hash, full_name, phone, user_type)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, password_hash, full_name, phone, user_type))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user and return user data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            SELECT id, email, full_name, phone, user_type, profile_complete, is_verified
            FROM users 
            WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        user = cursor.fetchone()
        conn.close()
        
        if user:
            return {
                'id': user[0],
                'email': user[1],
                'full_name': user[2],
                'phone': user[3],
                'user_type': user[4],
                'profile_complete': user[5],
                'is_verified': user[6]
            }
        return None
    
    def create_employer(self, email: str, password: str, company_name: str, company_type: str, contact_person: str) -> bool:
        """Create a new employer"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            
            cursor.execute('''
                INSERT INTO employers (email, password_hash, company_name, company_type, contact_person)
                VALUES (?, ?, ?, ?, ?)
            ''', (email, password_hash, company_name, company_type, contact_person))
            
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_employer(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate employer and return employer data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        password_hash = self.hash_password(password)
        
        cursor.execute('''
            SELECT id, email, company_name, company_type, contact_person, is_verified
            FROM employers 
            WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        employer = cursor.fetchone()
        conn.close()
        
        if employer:
            return {
                'id': employer[0],
                'email': employer[1],
                'company_name': employer[2],
                'company_type': employer[3],
                'contact_person': employer[4],
                'is_verified': employer[5]
            }
        return None
    
    def create_job(self, employer_id: int, title: str, description: str, location: str, 
                   job_type: str, salary_range: str, skills_required: List[str], 
                   requirements: str = "", category: str = "", application_deadline: str = None) -> int:
        """Create a new job posting"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Auto-expire date (30 days from now)
        auto_expire = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        cursor.execute('''
            INSERT INTO jobs (employer_id, title, description, requirements, location, 
                            job_type, salary_range, skills_required, application_deadline, 
                            category, auto_expire_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (employer_id, title, description, requirements, location, job_type, 
              salary_range, json.dumps(skills_required), application_deadline, category, auto_expire))
        
        job_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return job_id
    
    def get_jobs(self, filters: Dict = None, limit: int = 50) -> List[Dict]:
        """Get jobs with optional filters"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT j.*, e.company_name, e.company_type, e.is_verified as employer_verified
            FROM jobs j
            JOIN employers e ON j.employer_id = e.id
            WHERE j.is_active = 1 AND (j.auto_expire_date > date('now') OR j.auto_expire_date IS NULL)
        '''
        params = []
        
        if filters:
            if filters.get('location'):
                query += " AND j.location LIKE ?"
                params.append(f"%{filters['location']}%")
            
            if filters.get('job_type'):
                query += " AND j.job_type = ?"
                params.append(filters['job_type'])
            
            if filters.get('category'):
                query += " AND j.category = ?"
                params.append(filters['category'])
            
            if filters.get('skills'):
                query += " AND j.skills_required LIKE ?"
                params.append(f"%{filters['skills']}%")
        
        query += " ORDER BY j.created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        jobs = cursor.fetchall()
        conn.close()
        
        job_list = []
        for job in jobs:
            job_dict = {
                'id': job[0],
                'employer_id': job[1],
                'title': job[2],
                'description': job[3],
                'requirements': job[4],
                'location': job[5],
                'job_type': job[6],
                'experience_level': job[7],
                'salary_range': job[8],
                'skills_required': json.loads(job[9]) if job[9] else [],
                'benefits': job[10],
                'application_deadline': job[11],
                'is_active': job[12],
                'is_verified': job[13],
                'created_at': job[14],
                'updated_at': job[15],
                'view_count': job[16],
                'application_count': job[17],
                'category': job[18],
                'is_premium': job[19],
                'auto_expire_date': job[20],
                'company_name': job[21],
                'company_type': job[22],
                'employer_verified': job[23]
            }
            job_list.append(job_dict)
        
        return job_list
    
    def apply_for_job(self, job_id: int, user_id: int, cover_letter: str = "") -> bool:
        """Apply for a job"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Check if user has already applied
            cursor.execute('''
                SELECT id FROM applications WHERE job_id = ? AND user_id = ?
            ''', (job_id, user_id))
            
            if cursor.fetchone():
                conn.close()
                return False  # Already applied
            
            cursor.execute('''
                INSERT INTO applications (job_id, user_id, cover_letter)
                VALUES (?, ?, ?)
            ''', (job_id, user_id, cover_letter))
            
            # Update application count
            cursor.execute('''
                UPDATE jobs SET application_count = application_count + 1 WHERE id = ?
            ''', (job_id,))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_user_applications(self, user_id: int) -> List[Dict]:
        """Get all applications for a user"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT a.*, j.title, j.location, j.salary_range, e.company_name
            FROM applications a
            JOIN jobs j ON a.job_id = j.id
            JOIN employers e ON j.employer_id = e.id
            WHERE a.user_id = ?
            ORDER BY a.applied_at DESC
        ''', (user_id,))
        
        applications = cursor.fetchall()
        conn.close()
        
        app_list = []
        for app in applications:
            app_dict = {
                'id': app[0],
                'job_id': app[1],
                'user_id': app[2],
                'cover_letter': app[3],
                'status': app[4],
                'applied_at': app[5],
                'updated_at': app[6],
                'employer_notes': app[7],
                'interview_scheduled': app[8],
                'job_title': app[9],
                'job_location': app[10],
                'salary_range': app[11],
                'company_name': app[12]
            }
            app_list.append(app_dict)
        
        return app_list
    
    def save_skill_assessment(self, user_id: int, skill_name: str, assessment_type: str, 
                            score: int, max_score: int) -> bool:
        """Save skill assessment result"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            expires_at = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d %H:%M:%S')
            
            cursor.execute('''
                INSERT INTO skill_assessments (user_id, skill_name, assessment_type, score, max_score, expires_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, skill_name, assessment_type, score, max_score, expires_at))
            
            conn.commit()
            conn.close()
            return True
        except:
            return False
    
    def get_user_skills(self, user_id: int) -> List[Dict]:
        """Get user's skill assessments"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM skill_assessments 
            WHERE user_id = ? AND expires_at > datetime('now')
            ORDER BY completed_at DESC
        ''', (user_id,))
        
        skills = cursor.fetchall()
        conn.close()
        
        skill_list = []
        for skill in skills:
            skill_dict = {
                'id': skill[0],
                'user_id': skill[1],
                'skill_name': skill[2],
                'assessment_type': skill[3],
                'score': skill[4],
                'max_score': skill[5],
                'certificate_url': skill[6],
                'completed_at': skill[7],
                'expires_at': skill[8]
            }
            skill_list.append(skill_dict)
        
        return skill_list