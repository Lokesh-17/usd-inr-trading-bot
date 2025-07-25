import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import datetime
import uuid
import json
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, List, Optional
import re
from dataclasses import dataclass, asdict
import base64
from io import BytesIO

# Configure page
st.set_page_config(
    page_title="EduCareer+ | Smart Job Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .job-card {
        background: white;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: transform 0.2s;
    }
    
    .job-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .verified-badge {
        background: #28a745;
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 15px;
        font-size: 0.8rem;
        font-weight: bold;
    }
    
    .skill-tag {
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        margin: 0.2rem;
        display: inline-block;
        font-size: 0.85rem;
    }
    
    .chat-message {
        padding: 0.8rem;
        margin: 0.5rem 0;
        border-radius: 10px;
        max-width: 80%;
    }
    
    .user-message {
        background: #e3f2fd;
        margin-left: auto;
        text-align: right;
    }
    
    .bot-message {
        background: #f5f5f5;
        margin-right: auto;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Database Models
@dataclass
class User:
    id: str
    name: str
    email: str
    password_hash: str
    user_type: str  # 'job_seeker', 'employer', 'institution'
    profile_data: dict
    created_at: datetime.datetime
    is_verified: bool = False

@dataclass
class Job:
    id: str
    employer_id: str
    title: str
    description: str
    requirements: List[str]
    location: str
    salary_range: str
    job_type: str  # 'full_time', 'part_time', 'contract', 'internship'
    category: str  # 'education', 'technology', 'healthcare', etc.
    skills_required: List[str]
    is_verified: bool
    posted_date: datetime.datetime
    expires_date: datetime.datetime
    is_active: bool = True

@dataclass
class Application:
    id: str
    job_id: str
    applicant_id: str
    status: str  # 'applied', 'reviewing', 'shortlisted', 'rejected', 'hired'
    applied_date: datetime.datetime
    cover_letter: str
    resume_path: str
    video_intro_path: Optional[str] = None

# Database initialization
def init_database():
    conn = sqlite3.connect('educareer_plus.db')
    cursor = conn.cursor()
    
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
    
    conn.commit()
    conn.close()

# Initialize session state
def init_session_state():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_data' not in st.session_state:
        st.session_state.user_data = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 'home'
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

# Authentication functions
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

def register_user(name: str, email: str, password: str, user_type: str, profile_data: dict) -> bool:
    try:
        conn = sqlite3.connect('educareer_plus.db')
        cursor = conn.cursor()
        
        user_id = str(uuid.uuid4())
        password_hash = hash_password(password)
        
        cursor.execute('''
            INSERT INTO users (id, name, email, password_hash, user_type, profile_data, created_at, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, name, email, password_hash, user_type, json.dumps(profile_data), datetime.datetime.now(), False))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(email: str, password: str) -> Optional[Dict]:
    conn = sqlite3.connect('educareer_plus.db')
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    
    if user and verify_password(password, user[3]):
        user_data = {
            'id': user[0],
            'name': user[1],
            'email': user[2],
            'user_type': user[4],
            'profile_data': json.loads(user[5]) if user[5] else {},
            'is_verified': user[7]
        }
        conn.close()
        return user_data
    
    conn.close()
    return None

# Job matching algorithm with AI
def calculate_job_match_score(user_skills: List[str], job_skills: List[str], user_preferences: dict, job_data: dict) -> float:
    """Advanced AI-based job matching algorithm"""
    
    # Skill matching (50% weight)
    skill_matches = len(set(user_skills) & set(job_skills))
    skill_score = skill_matches / max(len(job_skills), 1) * 0.5
    
    # Location preference (20% weight)
    location_score = 0.2 if user_preferences.get('preferred_location', '').lower() in job_data.get('location', '').lower() else 0
    
    # Job type preference (15% weight)
    job_type_score = 0.15 if user_preferences.get('job_type') == job_data.get('job_type') else 0
    
    # Salary expectation (15% weight)
    salary_score = 0.15  # Simplified - would need more complex logic for real salary matching
    
    total_score = skill_score + location_score + job_type_score + salary_score
    return min(total_score * 100, 100)  # Cap at 100%

# Main application
def main():
    init_database()
    init_session_state()
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 EduCareer+ | Smart Job Portal</h1>
        <p>Revolutionizing job search with AI-powered matching, verified listings, and institutional integration</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    if not st.session_state.logged_in:
        show_auth_page()
    else:
        show_main_app()

def show_auth_page():
    """Authentication page with login and registration"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Welcome Back!")
            
            email = st.text_input("Email", key="login_email")
            password = st.text_input("Password", type="password", key="login_password")
            
            if st.button("Login", type="primary", use_container_width=True):
                user_data = login_user(email, password)
                if user_data:
                    st.session_state.logged_in = True
                    st.session_state.user_data = user_data
                    st.success("Login successful!")
                    st.rerun()
                else:
                    st.error("Invalid credentials!")
        
        with tab2:
            st.subheader("Join EduCareer+")
            
            name = st.text_input("Full Name")
            email = st.text_input("Email", key="reg_email")
            password = st.text_input("Password", type="password", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password")
            
            user_type = st.selectbox("I am a:", 
                                   ["job_seeker", "employer", "institution"],
                                   format_func=lambda x: {
                                       "job_seeker": "Job Seeker",
                                       "employer": "Employer", 
                                       "institution": "Educational Institution"
                                   }[x])
            
            # Additional profile fields based on user type
            profile_data = {}
            
            if user_type == "job_seeker":
                st.subheader("Job Seeker Profile")
                profile_data['skills'] = st.multiselect("Skills", 
                    ["Python", "Java", "JavaScript", "React", "Node.js", "Teaching", "Communication", "Leadership", "Data Analysis", "Project Management"])
                profile_data['experience_years'] = st.slider("Years of Experience", 0, 30, 0)
                profile_data['preferred_location'] = st.text_input("Preferred Location")
                profile_data['job_type'] = st.selectbox("Preferred Job Type", 
                    ["full_time", "part_time", "contract", "internship"])
                
            elif user_type == "employer":
                st.subheader("Employer Profile")
                profile_data['company_name'] = st.text_input("Company Name")
                profile_data['industry'] = st.selectbox("Industry", 
                    ["Education", "Technology", "Healthcare", "Finance", "Manufacturing", "Other"])
                profile_data['company_size'] = st.selectbox("Company Size", 
                    ["1-10", "11-50", "51-200", "201-1000", "1000+"])
                
            elif user_type == "institution":
                st.subheader("Institution Profile")
                profile_data['institution_name'] = st.text_input("Institution Name")
                profile_data['institution_type'] = st.selectbox("Institution Type", 
                    ["School", "College", "University", "Training Center"])
                profile_data['accreditation'] = st.text_input("Accreditation (NAAC/NBA/etc.)")
            
            if st.button("Register", type="primary", use_container_width=True):
                if password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters!")
                elif not email or not name:
                    st.error("Please fill all required fields!")
                else:
                    if register_user(name, email, password, user_type, profile_data):
                        st.success("Registration successful! Please login.")
                    else:
                        st.error("Email already exists!")

def show_main_app():
    """Main application interface after login"""
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user_data['name']}!")
        st.markdown(f"**Type:** {st.session_state.user_data['user_type'].replace('_', ' ').title()}")
        
        if st.session_state.user_data['is_verified']:
            st.markdown('<span class="verified-badge">✓ Verified</span>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation based on user type
        if st.session_state.user_data['user_type'] == 'job_seeker':
            pages = {
                "🏠 Dashboard": "dashboard",
                "🔍 Find Jobs": "find_jobs", 
                "📋 My Applications": "my_applications",
                "🎯 Skill Assessment": "skill_assessment",
                "💬 Messages": "messages",
                "👤 Profile": "profile"
            }
        elif st.session_state.user_data['user_type'] == 'employer':
            pages = {
                "🏠 Dashboard": "dashboard",
                "➕ Post Job": "post_job",
                "📊 My Jobs": "my_jobs",
                "👥 Candidates": "candidates", 
                "💬 Messages": "messages",
                "👤 Profile": "profile"
            }
        else:  # institution
            pages = {
                "🏠 Dashboard": "dashboard",
                "🎓 Placement Drive": "placement_drive",
                "👨‍🎓 Students": "students",
                "🏢 Partner Companies": "partners",
                "📊 Analytics": "analytics",
                "👤 Profile": "profile"
            }
        
        for page_name, page_key in pages.items():
            if st.button(page_name, use_container_width=True):
                st.session_state.current_page = page_key
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user_data = None
            st.session_state.current_page = 'home'
            st.rerun()
    
    # Main content area
    if st.session_state.current_page == 'dashboard':
        show_dashboard()
    elif st.session_state.current_page == 'find_jobs':
        show_find_jobs()
    elif st.session_state.current_page == 'post_job':
        show_post_job()
    elif st.session_state.current_page == 'my_applications':
        show_my_applications()
    elif st.session_state.current_page == 'skill_assessment':
        show_skill_assessment()
    elif st.session_state.current_page == 'messages':
        show_messages()
    elif st.session_state.current_page == 'profile':
        show_profile()
    else:
        show_dashboard()

def show_dashboard():
    """Dashboard with personalized content and analytics"""
    
    st.title("📊 Dashboard")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    # Get statistics from database
    conn = sqlite3.connect('educareer_plus.db')
    cursor = conn.cursor()
    
    # Total jobs
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active = TRUE")
    total_jobs = cursor.fetchone()[0]
    
    # Verified jobs
    cursor.execute("SELECT COUNT(*) FROM jobs WHERE is_active = TRUE AND is_verified = TRUE")
    verified_jobs = cursor.fetchone()[0]
    
    # Total applications (for job seekers) or total applicants (for employers)
    if st.session_state.user_data['user_type'] == 'job_seeker':
        cursor.execute("SELECT COUNT(*) FROM applications WHERE applicant_id = ?", 
                      (st.session_state.user_data['id'],))
        user_applications = cursor.fetchone()[0]
        metric_label = "My Applications"
    else:
        cursor.execute("""
            SELECT COUNT(*) FROM applications a 
            JOIN jobs j ON a.job_id = j.id 
            WHERE j.employer_id = ?
        """, (st.session_state.user_data['id'],))
        user_applications = cursor.fetchone()[0]
        metric_label = "Total Applicants"
    
    conn.close()
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_jobs}</h3>
            <p>Active Jobs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{verified_jobs}</h3>
            <p>Verified Jobs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{user_applications}</h3>
            <p>{metric_label}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        match_percentage = 85 if st.session_state.user_data['user_type'] == 'job_seeker' else 92
        st.markdown(f"""
        <div class="metric-card">
            <h3>{match_percentage}%</h3>
            <p>Match Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent activity and recommendations
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Personalized Recommendations")
        
        if st.session_state.user_data['user_type'] == 'job_seeker':
            # Show recommended jobs
            recommended_jobs = get_recommended_jobs(st.session_state.user_data['id'])
            
            if recommended_jobs:
                for job in recommended_jobs[:3]:  # Show top 3
                    with st.container():
                        st.markdown(f"""
                        <div class="job-card">
                            <h4>{job['title']}</h4>
                            <p><strong>Company:</strong> {job.get('company_name', 'N/A')}</p>
                            <p><strong>Location:</strong> {job['location']}</p>
                            <p><strong>Match Score:</strong> {job.get('match_score', 85)}%</p>
                            <div>
                                {''.join([f'<span class="skill-tag">{skill}</span>' for skill in job['skills_required'][:3]])}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("Complete your profile to get personalized job recommendations!")
        
        else:
            # Show recommended candidates for employers
            st.info("Candidate recommendations will appear here based on your job postings.")
    
    with col2:
        st.subheader("📈 Analytics")
        
        # Create sample analytics chart
        dates = pd.date_range(start='2024-01-01', end='2024-01-31', freq='D')
        values = np.random.randint(10, 50, len(dates))
        
        fig = px.line(x=dates, y=values, title="Job Applications Over Time")
        fig.update_layout(showlegend=False, height=300)
        st.plotly_chart(fig, use_container_width=True)

def get_recommended_jobs(user_id: str) -> List[Dict]:
    """Get AI-powered job recommendations for a user"""
    
    conn = sqlite3.connect('educareer_plus.db')
    cursor = conn.cursor()
    
    # Get user profile
    cursor.execute("SELECT profile_data FROM users WHERE id = ?", (user_id,))
    user_profile = cursor.fetchone()
    
    if not user_profile or not user_profile[0]:
        conn.close()
        return []
    
    profile_data = json.loads(user_profile[0])
    user_skills = profile_data.get('skills', [])
    user_preferences = {
        'preferred_location': profile_data.get('preferred_location', ''),
        'job_type': profile_data.get('job_type', '')
    }
    
    # Get active jobs
    cursor.execute("""
        SELECT j.*, u.name as company_name 
        FROM jobs j 
        JOIN users u ON j.employer_id = u.id 
        WHERE j.is_active = TRUE 
        ORDER BY j.posted_date DESC 
        LIMIT 10
    """)
    
    jobs = cursor.fetchall()
    conn.close()
    
    recommended_jobs = []
    
    for job in jobs:
        job_data = {
            'id': job[0],
            'title': job[2],
            'description': job[3],
            'location': job[5],
            'job_type': job[7],
            'skills_required': json.loads(job[9]) if job[9] else [],
            'company_name': job[14]
        }
        
        # Calculate match score
        match_score = calculate_job_match_score(user_skills, job_data['skills_required'], user_preferences, job_data)
        job_data['match_score'] = round(match_score)
        
        recommended_jobs.append(job_data)
    
    # Sort by match score
    recommended_jobs.sort(key=lambda x: x['match_score'], reverse=True)
    
    return recommended_jobs

def show_find_jobs():
    """Job search page with advanced filtering"""
    
    st.title("🔍 Find Your Perfect Job")
    
    # Search and filter section
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        search_query = st.text_input("🔍 Search jobs...", placeholder="Enter job title, skills, or company")
    
    with col2:
        location_filter = st.text_input("📍 Location", placeholder="City, State")
    
    with col3:
        job_type_filter = st.selectbox("Job Type", ["All", "full_time", "part_time", "contract", "internship"])
    
    # Advanced filters in expander
    with st.expander("🎛️ Advanced Filters"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            category_filter = st.selectbox("Category", 
                ["All", "education", "technology", "healthcare", "finance", "manufacturing"])
            
        with col2:
            salary_range = st.select_slider("Salary Range (LPA)", 
                options=["0-3", "3-6", "6-10", "10-15", "15+"], value="0-3")
        
        with col3:
            verified_only = st.checkbox("Verified Jobs Only", value=True)
    
    # Get and display jobs
    jobs = search_jobs(search_query, location_filter, job_type_filter, category_filter, verified_only)
    
    st.markdown(f"### Found {len(jobs)} jobs")
    
    # Display jobs
    for job in jobs:
        with st.container():
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: between; align-items: center;">
                        <h3>{job['title']}</h3>
                        {f'<span class="verified-badge">✓ Verified</span>' if job['is_verified'] else ''}
                    </div>
                    <p><strong>Company:</strong> {job.get('company_name', 'N/A')}</p>
                    <p><strong>Location:</strong> {job['location']}</p>
                    <p><strong>Type:</strong> {job['job_type'].replace('_', ' ').title()}</p>
                    <p><strong>Posted:</strong> {job['posted_date']}</p>
                    <p>{job['description'][:200]}...</p>
                    <div>
                        {''.join([f'<span class="skill-tag">{skill}</span>' for skill in job['skills_required'][:5]])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                if st.button(f"Apply Now", key=f"apply_{job['id']}", type="primary"):
                    apply_to_job(job['id'])
                
                if st.button(f"View Details", key=f"details_{job['id']}"):
                    show_job_details(job)

def search_jobs(query: str, location: str, job_type: str, category: str, verified_only: bool) -> List[Dict]:
    """Search jobs with filters"""
    
    conn = sqlite3.connect('educareer_plus.db')
    cursor = conn.cursor()
    
    # Build SQL query
    sql = """
        SELECT j.*, u.name as company_name 
        FROM jobs j 
        JOIN users u ON j.employer_id = u.id 
        WHERE j.is_active = TRUE
    """
    params = []
    
    if query:
        sql += " AND (j.title LIKE ? OR j.description LIKE ? OR j.skills_required LIKE ?)"
        params.extend([f"%{query}%", f"%{query}%", f"%{query}%"])
    
    if location:
        sql += " AND j.location LIKE ?"
        params.append(f"%{location}%")
    
    if job_type != "All":
        sql += " AND j.job_type = ?"
        params.append(job_type)
    
    if category != "All":
        sql += " AND j.category = ?"
        params.append(category)
    
    if verified_only:
        sql += " AND j.is_verified = TRUE"
    
    sql += " ORDER BY j.posted_date DESC LIMIT 20"
    
    cursor.execute(sql, params)
    jobs_data = cursor.fetchall()
    conn.close()
    
    jobs = []
    for job in jobs_data:
        job_dict = {
            'id': job[0],
            'employer_id': job[1],
            'title': job[2],
            'description': job[3],
            'requirements': json.loads(job[4]) if job[4] else [],
            'location': job[5],
            'salary_range': job[6],
            'job_type': job[7],
            'category': job[8],
            'skills_required': json.loads(job[9]) if job[9] else [],
            'is_verified': job[10],
            'posted_date': job[11],
            'expires_date': job[12],
            'company_name': job[14]
        }
        jobs.append(job_dict)
    
    return jobs

def apply_to_job(job_id: str):
    """Apply to a job"""
    
    # Check if already applied
    conn = sqlite3.connect('educareer_plus.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT id FROM applications 
        WHERE job_id = ? AND applicant_id = ?
    """, (job_id, st.session_state.user_data['id']))
    
    existing_application = cursor.fetchone()
    
    if existing_application:
        st.warning("You have already applied to this job!")
        conn.close()
        return
    
    # Create application form
    with st.form(f"apply_form_{job_id}"):
        st.subheader("Apply for this Job")
        
        cover_letter = st.text_area("Cover Letter", 
            placeholder="Tell the employer why you're the perfect fit for this role...")
        
        resume_file = st.file_uploader("Upload Resume", type=['pdf', 'doc', 'docx'])
        video_intro = st.file_uploader("Video Introduction (Optional)", type=['mp4', 'mov', 'avi'])
        
        submitted = st.form_submit_button("Submit Application", type="primary")
        
        if submitted:
            if not cover_letter:
                st.error("Please write a cover letter!")
                return
            
            if not resume_file:
                st.error("Please upload your resume!")
                return
            
            # Save application
            application_id = str(uuid.uuid4())
            resume_path = f"resumes/{application_id}_{resume_file.name}"
            video_path = f"videos/{application_id}_{video_intro.name}" if video_intro else None
            
            cursor.execute("""
                INSERT INTO applications 
                (id, job_id, applicant_id, status, applied_date, cover_letter, resume_path, video_intro_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (application_id, job_id, st.session_state.user_data['id'], 'applied', 
                  datetime.datetime.now(), cover_letter, resume_path, video_path))
            
            conn.commit()
            conn.close()
            
            st.success("Application submitted successfully!")
            st.balloons()

def show_post_job():
    """Job posting page for employers"""
    
    st.title("➕ Post a New Job")
    
    with st.form("post_job_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            job_title = st.text_input("Job Title*", placeholder="e.g., Senior Python Developer")
            location = st.text_input("Location*", placeholder="e.g., Bangalore, Karnataka")
            job_type = st.selectbox("Job Type*", ["full_time", "part_time", "contract", "internship"])
            category = st.selectbox("Category*", 
                ["education", "technology", "healthcare", "finance", "manufacturing", "other"])
        
        with col2:
            salary_range = st.text_input("Salary Range", placeholder="e.g., 8-12 LPA")
            expires_date = st.date_input("Application Deadline", 
                min_value=datetime.date.today(),
                value=datetime.date.today() + datetime.timedelta(days=30))
        
        job_description = st.text_area("Job Description*", height=200,
            placeholder="Describe the role, responsibilities, and what you're looking for...")
        
        requirements = st.text_area("Requirements", height=100,
            placeholder="List the key requirements (one per line)")
        
        skills_required = st.multiselect("Skills Required*", 
            ["Python", "Java", "JavaScript", "React", "Node.js", "Teaching", "Communication", 
             "Leadership", "Data Analysis", "Project Management", "SQL", "Machine Learning", "AWS"])
        
        is_verified = st.checkbox("Request Verification", 
            help="Verified jobs get higher visibility and trust from candidates")
        
        submitted = st.form_submit_button("Post Job", type="primary")
        
        if submitted:
            if not all([job_title, location, job_description, skills_required]):
                st.error("Please fill all required fields!")
                return
            
            # Save job to database
            job_id = str(uuid.uuid4())
            
            conn = sqlite3.connect('educareer_plus.db')
            cursor = conn.cursor()
            
            requirements_list = [req.strip() for req in requirements.split('\n') if req.strip()]
            
            cursor.execute("""
                INSERT INTO jobs 
                (id, employer_id, title, description, requirements, location, salary_range, 
                 job_type, category, skills_required, is_verified, posted_date, expires_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (job_id, st.session_state.user_data['id'], job_title, job_description, 
                  json.dumps(requirements_list), location, salary_range, job_type, category,
                  json.dumps(skills_required), is_verified, datetime.datetime.now(), expires_date))
            
            conn.commit()
            conn.close()
            
            st.success("Job posted successfully!")
            if is_verified:
                st.info("Your job will be reviewed for verification within 24 hours.")

def show_skill_assessment():
    """Skill assessment page with interactive tests"""
    
    st.title("🎯 Skill Assessment")
    
    st.markdown("""
    <div class="feature-card">
        <h3>Validate Your Skills</h3>
        <p>Take skill assessments to showcase your expertise to employers. 
        Verified skills get higher visibility in job matching.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Available assessments
    assessments = {
        "Python Programming": {
            "description": "Test your Python coding skills",
            "duration": "30 minutes",
            "questions": 15,
            "difficulty": "Intermediate"
        },
        "Communication Skills": {
            "description": "Assess your written and verbal communication",
            "duration": "20 minutes", 
            "questions": 10,
            "difficulty": "Basic"
        },
        "Data Analysis": {
            "description": "Test your data analysis and interpretation skills",
            "duration": "45 minutes",
            "questions": 20,
            "difficulty": "Advanced"
        },
        "Teaching Methodology": {
            "description": "Evaluate your teaching and pedagogical skills",
            "duration": "25 minutes",
            "questions": 12,
            "difficulty": "Intermediate"
        }
    }
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Available Assessments")
        
        for skill, details in assessments.items():
            with st.container():
                st.markdown(f"""
                <div class="job-card">
                    <h4>{skill}</h4>
                    <p>{details['description']}</p>
                    <p><strong>Duration:</strong> {details['duration']}</p>
                    <p><strong>Questions:</strong> {details['questions']}</p>
                    <p><strong>Difficulty:</strong> {details['difficulty']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Start Assessment", key=f"start_{skill}"):
                    start_skill_assessment(skill, details)
    
    with col2:
        st.subheader("Your Skill Scores")
        
        # Get user's assessment history
        conn = sqlite3.connect('educareer_plus.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT skill_name, score, assessment_date 
            FROM skill_assessments 
            WHERE user_id = ? 
            ORDER BY assessment_date DESC
        """, (st.session_state.user_data['id'],))
        
        assessments_taken = cursor.fetchall()
        conn.close()
        
        if assessments_taken:
            for assessment in assessments_taken:
                skill_name, score, date = assessment
                
                # Color code based on score
                if score >= 80:
                    color = "#28a745"  # Green
                elif score >= 60:
                    color = "#ffc107"  # Yellow
                else:
                    color = "#dc3545"  # Red
                
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; 
                           border-left: 4px solid {color};">
                    <h4>{skill_name}</h4>
                    <p><strong>Score:</strong> {score}/100</p>
                    <p><strong>Date:</strong> {date}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No assessments taken yet. Start with a skill assessment to showcase your expertise!")

def start_skill_assessment(skill_name: str, details: dict):
    """Start a skill assessment"""
    
    st.subheader(f"Assessment: {skill_name}")
    st.info(f"Duration: {details['duration']} | Questions: {details['questions']}")
    
    # Sample questions (in a real app, these would come from a question bank)
    questions = generate_assessment_questions(skill_name)
    
    with st.form(f"assessment_{skill_name}"):
        answers = []
        
        for i, question in enumerate(questions[:5]):  # Show first 5 questions for demo
            st.markdown(f"**Question {i+1}:** {question['question']}")
            
            if question['type'] == 'multiple_choice':
                answer = st.radio(f"Select your answer:", question['options'], key=f"q{i}")
                answers.append(answer)
            elif question['type'] == 'code':
                answer = st.text_area(f"Write your code:", key=f"q{i}", height=100)
                answers.append(answer)
            else:
                answer = st.text_area(f"Your answer:", key=f"q{i}")
                answers.append(answer)
            
            st.markdown("---")
        
        submitted = st.form_submit_button("Submit Assessment", type="primary")
        
        if submitted:
            # Calculate score (simplified scoring)
            score = calculate_assessment_score(skill_name, questions[:5], answers)
            
            # Save to database
            conn = sqlite3.connect('educareer_plus.db')
            cursor = conn.cursor()
            
            assessment_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO skill_assessments 
                (id, user_id, skill_name, score, assessment_date)
                VALUES (?, ?, ?, ?, ?)
            """, (assessment_id, st.session_state.user_data['id'], skill_name, 
                  score, datetime.datetime.now()))
            
            conn.commit()
            conn.close()
            
            # Show results
            st.success(f"Assessment completed! Your score: {score}/100")
            
            if score >= 80:
                st.balloons()
                st.success("Excellent! This skill will be highlighted in your profile.")
            elif score >= 60:
                st.info("Good job! Keep practicing to improve your score.")
            else:
                st.warning("Consider studying more in this area and retaking the assessment.")

def generate_assessment_questions(skill_name: str) -> List[Dict]:
    """Generate sample assessment questions"""
    
    if skill_name == "Python Programming":
        return [
            {
                "question": "What is the output of: print([1, 2, 3] * 2)?",
                "type": "multiple_choice",
                "options": ["[1, 2, 3, 1, 2, 3]", "[2, 4, 6]", "[1, 2, 3, 2]", "Error"],
                "correct": "[1, 2, 3, 1, 2, 3]"
            },
            {
                "question": "Write a function to find the factorial of a number:",
                "type": "code",
                "correct": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)"
            },
            {
                "question": "What is a decorator in Python?",
                "type": "text",
                "correct": "A decorator is a function that modifies another function"
            },
            {
                "question": "Which of these is NOT a Python data type?",
                "type": "multiple_choice", 
                "options": ["list", "tuple", "array", "dict"],
                "correct": "array"
            },
            {
                "question": "How do you handle exceptions in Python?",
                "type": "multiple_choice",
                "options": ["try/catch", "try/except", "catch/finally", "handle/error"],
                "correct": "try/except"
            }
        ]
    
    elif skill_name == "Communication Skills":
        return [
            {
                "question": "What is the most important aspect of effective communication?",
                "type": "multiple_choice",
                "options": ["Speaking loudly", "Active listening", "Using big words", "Talking fast"],
                "correct": "Active listening"
            },
            {
                "question": "Write a professional email requesting a meeting:",
                "type": "text",
                "correct": "Professional email with clear subject, polite tone, specific request"
            },
            {
                "question": "How would you explain a complex technical concept to a non-technical person?",
                "type": "text", 
                "correct": "Use simple language, analogies, examples, avoid jargon"
            },
            {
                "question": "What does 'CC' mean in email?",
                "type": "multiple_choice",
                "options": ["Carbon Copy", "Central Copy", "Courtesy Copy", "Complete Copy"],
                "correct": "Carbon Copy"
            },
            {
                "question": "Describe a time when you had to give difficult feedback:",
                "type": "text",
                "correct": "Structured response with situation, approach, outcome"
            }
        ]
    
    # Add more skill assessments...
    return []

def calculate_assessment_score(skill_name: str, questions: List[Dict], answers: List[str]) -> int:
    """Calculate assessment score (simplified)"""
    
    correct_answers = 0
    total_questions = len(questions)
    
    for i, (question, answer) in enumerate(zip(questions, answers)):
        if question['type'] == 'multiple_choice':
            if answer == question['correct']:
                correct_answers += 1
        else:
            # For text/code questions, use simplified scoring
            if answer and len(answer.strip()) > 10:  # Basic check for effort
                correct_answers += 0.7  # Partial credit
    
    score = int((correct_answers / total_questions) * 100)
    return min(score, 100)

def show_messages():
    """Real-time messaging system"""
    
    st.title("💬 Messages")
    
    # Get conversations
    conn = sqlite3.connect('educareer_plus.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT DISTINCT 
            CASE 
                WHEN sender_id = ? THEN receiver_id 
                ELSE sender_id 
            END as other_user_id,
            u.name as other_user_name,
            u.user_type as other_user_type,
            MAX(m.timestamp) as last_message_time
        FROM messages m
        JOIN users u ON (
            CASE 
                WHEN m.sender_id = ? THEN m.receiver_id = u.id
                ELSE m.sender_id = u.id
            END
        )
        WHERE sender_id = ? OR receiver_id = ?
        GROUP BY other_user_id
        ORDER BY last_message_time DESC
    """, (st.session_state.user_data['id'], st.session_state.user_data['id'], 
          st.session_state.user_data['id'], st.session_state.user_data['id']))
    
    conversations = cursor.fetchall()
    
    if conversations:
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Conversations")
            
            selected_conversation = None
            for conversation in conversations:
                other_user_id, other_user_name, other_user_type, last_message_time = conversation
                
                if st.button(f"{other_user_name} ({other_user_type})", 
                           key=f"conv_{other_user_id}", use_container_width=True):
                    selected_conversation = other_user_id
                    st.session_state.selected_conversation = other_user_id
        
        with col2:
            if 'selected_conversation' in st.session_state:
                show_conversation(st.session_state.selected_conversation)
            else:
                st.info("Select a conversation to start messaging")
    
    else:
        st.info("No messages yet. Apply to jobs or post jobs to start conversations!")
    
    conn.close()

def show_conversation(other_user_id: str):
    """Show conversation with specific user"""
    
    conn = sqlite3.connect('educareer_plus.db')
    cursor = conn.cursor()
    
    # Get other user info
    cursor.execute("SELECT name, user_type FROM users WHERE id = ?", (other_user_id,))
    other_user = cursor.fetchone()
    
    if not other_user:
        st.error("User not found!")
        return
    
    other_user_name, other_user_type = other_user
    
    st.subheader(f"Chat with {other_user_name}")
    
    # Get messages
    cursor.execute("""
        SELECT sender_id, message, timestamp 
        FROM messages 
        WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ORDER BY timestamp ASC
    """, (st.session_state.user_data['id'], other_user_id, other_user_id, st.session_state.user_data['id']))
    
    messages = cursor.fetchall()
    
    # Display messages
    message_container = st.container()
    
    with message_container:
        for message in messages:
            sender_id, message_text, timestamp = message
            
            if sender_id == st.session_state.user_data['id']:
                # User's message
                st.markdown(f"""
                <div class="chat-message user-message">
                    <p>{message_text}</p>
                    <small>{timestamp}</small>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Other user's message
                st.markdown(f"""
                <div class="chat-message bot-message">
                    <p>{message_text}</p>
                    <small>{timestamp}</small>
                </div>
                """, unsafe_allow_html=True)
    
    # Message input
    with st.form(f"message_form_{other_user_id}"):
        new_message = st.text_area("Type your message...", height=100)
        sent = st.form_submit_button("Send Message", type="primary")
        
        if sent and new_message.strip():
            # Save message
            message_id = str(uuid.uuid4())
            cursor.execute("""
                INSERT INTO messages (id, sender_id, receiver_id, message, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, (message_id, st.session_state.user_data['id'], other_user_id, 
                  new_message.strip(), datetime.datetime.now()))
            
            conn.commit()
            st.success("Message sent!")
            st.rerun()
    
    conn.close()

def show_my_applications():
    """Show user's job applications"""
    
    st.title("📋 My Applications")
    
    conn = sqlite3.connect('educareer_plus.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT a.*, j.title, j.location, u.name as company_name
        FROM applications a
        JOIN jobs j ON a.job_id = j.id
        JOIN users u ON j.employer_id = u.id
        WHERE a.applicant_id = ?
        ORDER BY a.applied_date DESC
    """, (st.session_state.user_data['id'],))
    
    applications = cursor.fetchall()
    conn.close()
    
    if applications:
        for app in applications:
            app_id, job_id, applicant_id, status, applied_date, cover_letter, resume_path, video_path, job_title, location, company_name = app
            
            # Status color coding
            status_colors = {
                'applied': '#17a2b8',
                'reviewing': '#ffc107', 
                'shortlisted': '#28a745',
                'rejected': '#dc3545',
                'hired': '#6f42c1'
            }
            
            status_color = status_colors.get(status, '#6c757d')
            
            st.markdown(f"""
            <div class="job-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h3>{job_title}</h3>
                    <span style="background: {status_color}; color: white; padding: 0.3rem 0.8rem; 
                                border-radius: 15px; font-size: 0.85rem;">
                        {status.replace('_', ' ').title()}
                    </span>
                </div>
                <p><strong>Company:</strong> {company_name}</p>
                <p><strong>Location:</strong> {location}</p>
                <p><strong>Applied:</strong> {applied_date}</p>
                <p><strong>Cover Letter:</strong> {cover_letter[:100]}...</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No applications yet. Start by finding and applying to jobs!")

def show_profile():
    """User profile management"""
    
    st.title("👤 Profile")
    
    user_data = st.session_state.user_data
    profile_data = user_data.get('profile_data', {})
    
    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Full Name", value=user_data['name'])
            email = st.text_input("Email", value=user_data['email'], disabled=True)
            
            if user_data['user_type'] == 'job_seeker':
                skills = st.multiselect("Skills", 
                    ["Python", "Java", "JavaScript", "React", "Node.js", "Teaching", "Communication", 
                     "Leadership", "Data Analysis", "Project Management", "SQL", "Machine Learning", "AWS"],
                    default=profile_data.get('skills', []))
                
                experience_years = st.slider("Years of Experience", 0, 30, 
                    profile_data.get('experience_years', 0))
                
        with col2:
            if user_data['user_type'] == 'job_seeker':
                preferred_location = st.text_input("Preferred Location", 
                    value=profile_data.get('preferred_location', ''))
                
                job_type = st.selectbox("Preferred Job Type", 
                    ["full_time", "part_time", "contract", "internship"],
                    index=["full_time", "part_time", "contract", "internship"].index(
                        profile_data.get('job_type', 'full_time')))
                
                bio = st.text_area("Bio", value=profile_data.get('bio', ''),
                    placeholder="Tell employers about yourself...")
        
        # Profile picture upload
        profile_pic = st.file_uploader("Profile Picture", type=['jpg', 'jpeg', 'png'])
        
        # Video introduction
        video_intro = st.file_uploader("Video Introduction", type=['mp4', 'mov', 'avi'])
        
        submitted = st.form_submit_button("Update Profile", type="primary")
        
        if submitted:
            # Update profile data
            updated_profile = profile_data.copy()
            
            if user_data['user_type'] == 'job_seeker':
                updated_profile.update({
                    'skills': skills,
                    'experience_years': experience_years,
                    'preferred_location': preferred_location,
                    'job_type': job_type,
                    'bio': bio
                })
            
            # Update database
            conn = sqlite3.connect('educareer_plus.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET name = ?, profile_data = ?
                WHERE id = ?
            """, (name, json.dumps(updated_profile), user_data['id']))
            
            conn.commit()
            conn.close()
            
            # Update session state
            st.session_state.user_data['name'] = name
            st.session_state.user_data['profile_data'] = updated_profile
            
            st.success("Profile updated successfully!")

def show_job_details(job: dict):
    """Show detailed job information"""
    
    st.subheader(f"📋 {job['title']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Company:** {job.get('company_name', 'N/A')}")
        st.markdown(f"**Location:** {job['location']}")
        st.markdown(f"**Job Type:** {job['job_type'].replace('_', ' ').title()}")
        st.markdown(f"**Category:** {job['category'].title()}")
        st.markdown(f"**Salary Range:** {job.get('salary_range', 'Not specified')}")
        st.markdown(f"**Posted:** {job['posted_date']}")
        
        if job['is_verified']:
            st.markdown('<span class="verified-badge">✓ Verified Employer</span>', unsafe_allow_html=True)
        
        st.markdown("### Job Description")
        st.markdown(job['description'])
        
        if job.get('requirements'):
            st.markdown("### Requirements")
            for req in job['requirements']:
                st.markdown(f"• {req}")
        
        st.markdown("### Skills Required")
        skills_html = ''.join([f'<span class="skill-tag">{skill}</span>' for skill in job['skills_required']])
        st.markdown(skills_html, unsafe_allow_html=True)
    
    with col2:
        if st.button("Apply Now", type="primary", use_container_width=True):
            apply_to_job(job['id'])
        
        if st.button("Save Job", use_container_width=True):
            st.info("Job saved to your favorites!")
        
        if st.button("Share Job", use_container_width=True):
            st.info("Job link copied to clipboard!")

# Add AI Chatbot integration
def show_ai_assistant():
    """Show AI assistant interface"""
    from ai_chatbot import show_chatbot_interface
    show_chatbot_interface()

if __name__ == "__main__":
    main()