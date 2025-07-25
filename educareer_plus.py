import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
from database import JobPortalDB
from ai_matching import AIJobMatcher, SkillAssessment
from streamlit_option_menu import option_menu
import time

# Page configuration
st.set_page_config(
    page_title="EduCareer+ | Smart Job Portal",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database and AI components
@st.cache_resource
def init_components():
    db = JobPortalDB()
    ai_matcher = AIJobMatcher()
    skill_assessor = SkillAssessment()
    return db, ai_matcher, skill_assessor

db, ai_matcher, skill_assessor = init_components()

# Custom CSS for modern UI
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .job-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    .skill-badge {
        background: #e3f2fd;
        color: #1976d2;
        padding: 0.25rem 0.75rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.25rem;
        display: inline-block;
    }
    
    .match-score {
        background: linear-gradient(45deg, #4caf50, #8bc34a);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        text-align: center;
    }
    
    .verified-badge {
        background: #4caf50;
        color: white;
        padding: 0.25rem 0.5rem;
        border-radius: 10px;
        font-size: 0.7rem;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Session state initialization
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_type' not in st.session_state:
    st.session_state.user_type = None
if 'user_data' not in st.session_state:
    st.session_state.user_data = None

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎓 EduCareer+ | Smart Job Portal</h1>
        <p>Bridging Education and Employment with AI-Powered Matching</p>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.logged_in:
        show_auth_page()
    else:
        if st.session_state.user_type == 'job_seeker':
            show_job_seeker_dashboard()
        elif st.session_state.user_type == 'employer':
            show_employer_dashboard()
        elif st.session_state.user_type == 'institution':
            show_institution_dashboard()

def show_auth_page():
    """Authentication page with login and registration"""
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### Welcome to EduCareer+")
        
        tab1, tab2, tab3 = st.tabs(["🔐 Login", "👤 Job Seeker Signup", "🏢 Employer Signup"])
        
        with tab1:
            st.markdown("#### Login to Your Account")
            
            user_type = st.selectbox("Select User Type", ["Job Seeker", "Employer", "Institution"])
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            
            if st.button("Login", type="primary", use_container_width=True):
                if user_type == "Job Seeker":
                    user = db.authenticate_user(email, password)
                    if user:
                        st.session_state.logged_in = True
                        st.session_state.user_type = 'job_seeker'
                        st.session_state.user_data = user
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")
                
                elif user_type == "Employer":
                    employer = db.authenticate_employer(email, password)
                    if employer:
                        st.session_state.logged_in = True
                        st.session_state.user_type = 'employer'
                        st.session_state.user_data = employer
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error("Invalid credentials!")
        
        with tab2:
            st.markdown("#### Create Job Seeker Account")
            
            full_name = st.text_input("Full Name", key="js_name")
            email = st.text_input("Email Address", key="js_email")
            phone = st.text_input("Phone Number", key="js_phone")
            password = st.text_input("Password", type="password", key="js_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="js_confirm")
            
            if st.button("Create Account", type="primary", use_container_width=True, key="js_signup"):
                if password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters!")
                else:
                    if db.create_user(email, password, full_name, phone):
                        st.success("Account created successfully! Please login.")
                    else:
                        st.error("Email already exists!")
        
        with tab3:
            st.markdown("#### Create Employer Account")
            
            company_name = st.text_input("Company/Institution Name", key="emp_company")
            company_type = st.selectbox("Organization Type", 
                                      ["School", "College", "University", "Company", "NGO", "Startup"], 
                                      key="emp_type")
            contact_person = st.text_input("Contact Person Name", key="emp_contact")
            email = st.text_input("Official Email", key="emp_email")
            password = st.text_input("Password", type="password", key="emp_password")
            confirm_password = st.text_input("Confirm Password", type="password", key="emp_confirm")
            
            if st.button("Create Account", type="primary", use_container_width=True, key="emp_signup"):
                if password != confirm_password:
                    st.error("Passwords don't match!")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters!")
                else:
                    if db.create_employer(email, password, company_name, company_type.lower(), contact_person):
                        st.success("Employer account created successfully! Please login.")
                    else:
                        st.error("Email already exists!")

def show_job_seeker_dashboard():
    """Job seeker dashboard with AI recommendations and skill assessments"""
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user_data['full_name']}!")
        
        selected = option_menu(
            menu_title="Navigation",
            options=["🏠 Dashboard", "🔍 Browse Jobs", "🎯 AI Recommendations", 
                    "📊 Skill Assessment", "📝 My Applications", "👤 Profile", "💬 Messages"],
            icons=["house", "search", "bullseye", "graph-up", "file-text", "person", "chat"],
            menu_icon="cast",
            default_index=0,
        )
        
        if st.button("Logout", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.user_data = None
            st.rerun()
    
    if selected == "🏠 Dashboard":
        show_job_seeker_home()
    elif selected == "🔍 Browse Jobs":
        show_browse_jobs()
    elif selected == "🎯 AI Recommendations":
        show_ai_recommendations()
    elif selected == "📊 Skill Assessment":
        show_skill_assessment()
    elif selected == "📝 My Applications":
        show_my_applications()
    elif selected == "👤 Profile":
        show_user_profile()
    elif selected == "💬 Messages":
        show_messages()

def show_job_seeker_home():
    """Job seeker home dashboard"""
    st.markdown("### 🏠 Your Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    user_id = st.session_state.user_data['id']
    applications = db.get_user_applications(user_id)
    skills = db.get_user_skills(user_id)
    
    with col1:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{len(applications)}</h3>
            <p>Applications</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{len(skills)}</h3>
            <p>Skills Verified</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        profile_completion = 75 if st.session_state.user_data.get('profile_complete') else 25
        st.markdown(f"""
        <div class="stats-card">
            <h3>{profile_completion}%</h3>
            <p>Profile Complete</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stats-card">
            <h3>{'✅' if st.session_state.user_data.get('is_verified') else '⏳'}</h3>
            <p>Verification</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent applications chart
    if applications:
        st.markdown("### 📈 Application Status Overview")
        
        status_counts = {}
        for app in applications:
            status = app['status']
            status_counts[status] = status_counts.get(status, 0) + 1
        
        fig = px.pie(
            values=list(status_counts.values()),
            names=list(status_counts.keys()),
            title="Application Status Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Quick actions
    st.markdown("### ⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Browse Latest Jobs", use_container_width=True):
            st.session_state.selected_page = "browse_jobs"
            st.rerun()
    
    with col2:
        if st.button("🎯 Get AI Recommendations", use_container_width=True):
            st.session_state.selected_page = "ai_recommendations"
            st.rerun()
    
    with col3:
        if st.button("📊 Take Skill Test", use_container_width=True):
            st.session_state.selected_page = "skill_assessment"
            st.rerun()

def show_browse_jobs():
    """Browse jobs with advanced filtering"""
    st.markdown("### 🔍 Browse Jobs")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        location_filter = st.text_input("Location", placeholder="e.g., Bangalore, Mumbai")
    
    with col2:
        job_type_filter = st.selectbox("Job Type", ["All", "Full-time", "Part-time", "Contract", "Internship"])
    
    with col3:
        category_filter = st.selectbox("Category", ["All", "Teaching", "Technical", "Administrative", "Research"])
    
    with col4:
        skills_filter = st.text_input("Skills", placeholder="e.g., Python, Teaching")
    
    # Build filters dictionary
    filters = {}
    if location_filter:
        filters['location'] = location_filter
    if job_type_filter != "All":
        filters['job_type'] = job_type_filter.lower()
    if category_filter != "All":
        filters['category'] = category_filter.lower()
    if skills_filter:
        filters['skills'] = skills_filter
    
    # Get jobs
    jobs = db.get_jobs(filters=filters, limit=20)
    
    st.markdown(f"### Found {len(jobs)} jobs")
    
    # Display jobs
    for job in jobs:
        with st.container():
            st.markdown(f"""
            <div class="job-card">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h4>{job['title']}</h4>
                        <p><strong>{job['company_name']}</strong> 
                        {'<span class="verified-badge">✓ Verified</span>' if job['employer_verified'] else ''}
                        </p>
                        <p>📍 {job['location']} | 💼 {job['job_type'].title()} | 💰 {job['salary_range']}</p>
                    </div>
                    <div style="text-align: right;">
                        <p><small>Posted: {job['created_at'][:10]}</small></p>
                        <p><small>👥 {job['application_count']} applications</small></p>
                    </div>
                </div>
                
                <p>{job['description'][:200]}...</p>
                
                <div style="margin: 1rem 0;">
                    {''.join([f'<span class="skill-badge">{skill}</span>' for skill in job['skills_required'][:5]])}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if st.button(f"View Details", key=f"view_{job['id']}"):
                    show_job_details(job)
            with col2:
                if st.button(f"Apply Now", key=f"apply_{job['id']}", type="primary"):
                    apply_for_job(job)

def show_ai_recommendations():
    """AI-powered job recommendations"""
    st.markdown("### 🎯 AI-Powered Job Recommendations")
    
    # Get user profile (simplified for demo)
    user_profile = {
        'skills': ['Python', 'Teaching', 'Communication'],
        'location': 'Bangalore',
        'experience_years': 2,
        'bio': 'Experienced teacher with programming skills',
        'preferences': {'preferred_job_types': ['full-time', 'remote']},
        'salary_expectation': '5 LPA'
    }
    
    # Get all jobs for recommendation
    all_jobs = db.get_jobs(limit=100)
    
    if all_jobs:
        # Get AI recommendations
        recommendations = ai_matcher.get_job_recommendations(user_profile, all_jobs, top_k=10)
        
        st.markdown(f"### 🎯 Top {len(recommendations)} AI-Matched Jobs for You")
        
        for i, rec in enumerate(recommendations, 1):
            job = rec['job']
            match_score = rec['match_score']
            reasons = rec['reasons']
            
            with st.container():
                st.markdown(f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div style="flex: 1;">
                            <div style="display: flex; align-items: center; gap: 1rem;">
                                <h4>#{i} {job['title']}</h4>
                                <div class="match-score">
                                    {int(match_score * 100)}% Match
                                </div>
                            </div>
                            <p><strong>{job['company_name']}</strong> 
                            {'<span class="verified-badge">✓ Verified</span>' if job['employer_verified'] else ''}
                            </p>
                            <p>📍 {job['location']} | 💼 {job['job_type'].title()} | 💰 {job['salary_range']}</p>
                        </div>
                    </div>
                    
                    <p>{job['description'][:200]}...</p>
                    
                    <div style="margin: 1rem 0;">
                        <strong>🎯 Why this matches you:</strong>
                        <ul>
                            {''.join([f'<li>{reason}</li>' for reason in reasons])}
                        </ul>
                    </div>
                    
                    <div style="margin: 1rem 0;">
                        {''.join([f'<span class="skill-badge">{skill}</span>' for skill in job['skills_required'][:5]])}
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    if st.button(f"View Details", key=f"ai_view_{job['id']}"):
                        show_job_details(job)
                with col2:
                    if st.button(f"Apply Now", key=f"ai_apply_{job['id']}", type="primary"):
                        apply_for_job(job)
    else:
        st.info("No jobs available for recommendations at the moment.")

def show_skill_assessment():
    """Skill assessment module"""
    st.markdown("### 📊 Skill Assessment Center")
    
    st.markdown("""
    Take skill assessments to validate your expertise and improve your job match score!
    """)
    
    # Assessment categories
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 💻 Technical Skills")
        if st.button("Python Assessment", use_container_width=True):
            take_coding_assessment("python")
        if st.button("JavaScript Assessment", use_container_width=True):
            take_coding_assessment("javascript")
    
    with col2:
        st.markdown("#### 🗣️ Communication Skills")
        if st.button("Communication Assessment", use_container_width=True):
            take_communication_assessment()
    
    with col3:
        st.markdown("#### 🎓 Teaching Skills")
        if st.button("Teaching Assessment", use_container_width=True):
            take_teaching_assessment()
    
    # Show existing assessments
    user_id = st.session_state.user_data['id']
    existing_skills = db.get_user_skills(user_id)
    
    if existing_skills:
        st.markdown("### 🏆 Your Skill Certificates")
        
        for skill in existing_skills:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            
            with col1:
                st.markdown(f"**{skill['skill_name'].title()}**")
            with col2:
                st.markdown(f"Score: {skill['score']}/{skill['max_score']}")
            with col3:
                percentage = int((skill['score'] / skill['max_score']) * 100)
                if percentage >= 80:
                    st.success(f"{percentage}%")
                elif percentage >= 60:
                    st.warning(f"{percentage}%")
                else:
                    st.error(f"{percentage}%")
            with col4:
                st.markdown(f"<small>{skill['completed_at'][:10]}</small>", unsafe_allow_html=True)

def take_coding_assessment(skill):
    """Take a coding skill assessment"""
    st.markdown(f"### 💻 {skill.title()} Assessment")
    
    # Get questions for the skill
    questions = skill_assessor.coding_questions.get(skill, [])
    
    if not questions:
        st.error("No questions available for this skill.")
        return
    
    question_index = st.selectbox("Select Question", range(len(questions)), 
                                format_func=lambda x: f"Question {x+1} ({questions[x]['difficulty']})")
    
    question = questions[question_index]
    
    st.markdown(f"**Question:** {question['question']}")
    st.markdown(f"**Difficulty:** {question['difficulty'].title()}")
    st.markdown(f"**Max Score:** {question['max_score']}")
    
    # Code editor
    answer = st.text_area("Your Code:", height=200, placeholder="Write your code here...")
    
    if st.button("Submit Answer", type="primary"):
        if answer.strip():
            # Evaluate the answer
            result = skill_assessor.evaluate_coding_answer(skill, question_index, answer)
            
            # Save to database
            user_id = st.session_state.user_data['id']
            db.save_skill_assessment(user_id, skill, 'coding', result['score'], result['max_score'])
            
            st.success(f"Assessment completed! Score: {result['score']}/{result['max_score']}")
            st.markdown(f"**Feedback:** {result['feedback']}")
            
            # Show progress bar
            progress = result['score'] / result['max_score']
            st.progress(progress)
        else:
            st.error("Please provide an answer!")

def take_communication_assessment():
    """Take communication skill assessment"""
    st.markdown("### 🗣️ Communication Skills Assessment")
    
    questions = skill_assessor.communication_questions
    
    question_index = st.selectbox("Select Question", range(len(questions)), 
                                format_func=lambda x: f"Question {x+1}")
    
    question = questions[question_index]
    
    st.markdown(f"**Question:** {question['question']}")
    st.markdown(f"**Max Score:** {question['max_score']}")
    
    answer = st.text_area("Your Answer:", height=150, 
                         placeholder="Provide a detailed answer (aim for 50-100 words)...")
    
    if st.button("Submit Answer", type="primary"):
        if answer.strip():
            result = skill_assessor.evaluate_communication_answer(question_index, answer)
            
            user_id = st.session_state.user_data['id']
            db.save_skill_assessment(user_id, 'communication', 'communication', 
                                   result['score'], result['max_score'])
            
            st.success(f"Assessment completed! Score: {result['score']}/{result['max_score']}")
            st.markdown(f"**Feedback:** {result['feedback']}")
            
            progress = result['score'] / result['max_score']
            st.progress(progress)
        else:
            st.error("Please provide an answer!")

def take_teaching_assessment():
    """Take teaching skill assessment"""
    st.markdown("### 🎓 Teaching Skills Assessment")
    
    questions = skill_assessor.teaching_questions
    
    question_index = st.selectbox("Select Question", range(len(questions)), 
                                format_func=lambda x: f"Question {x+1}")
    
    question = questions[question_index]
    
    st.markdown(f"**Question:** {question['question']}")
    st.markdown(f"**Max Score:** {question['max_score']}")
    
    answer = st.text_area("Your Answer:", height=150, 
                         placeholder="Share your teaching philosophy and approach...")
    
    if st.button("Submit Answer", type="primary"):
        if answer.strip():
            result = skill_assessor.evaluate_teaching_answer(question_index, answer)
            
            user_id = st.session_state.user_data['id']
            db.save_skill_assessment(user_id, 'teaching', 'teaching', 
                                   result['score'], result['max_score'])
            
            st.success(f"Assessment completed! Score: {result['score']}/{result['max_score']}")
            st.markdown(f"**Feedback:** {result['feedback']}")
            
            progress = result['score'] / result['max_score']
            st.progress(progress)
        else:
            st.error("Please provide an answer!")

def show_my_applications():
    """Show user's job applications"""
    st.markdown("### 📝 My Applications")
    
    user_id = st.session_state.user_data['id']
    applications = db.get_user_applications(user_id)
    
    if applications:
        # Status filter
        status_filter = st.selectbox("Filter by Status", 
                                   ["All", "Applied", "Shortlisted", "Interviewed", "Hired", "Rejected"])
        
        filtered_apps = applications
        if status_filter != "All":
            filtered_apps = [app for app in applications if app['status'].lower() == status_filter.lower()]
        
        st.markdown(f"### {len(filtered_apps)} Applications")
        
        for app in filtered_apps:
            with st.container():
                st.markdown(f"""
                <div class="job-card">
                    <div style="display: flex; justify-content: space-between; align-items: start;">
                        <div>
                            <h4>{app['job_title']}</h4>
                            <p><strong>{app['company_name']}</strong></p>
                            <p>📍 {app['job_location']} | 💰 {app['salary_range']}</p>
                        </div>
                        <div style="text-align: right;">
                            <span class="skill-badge" style="background: {'#4caf50' if app['status'] == 'hired' else '#ff9800' if app['status'] == 'interviewed' else '#2196f3'};">
                                {app['status'].title()}
                            </span>
                            <p><small>Applied: {app['applied_at'][:10]}</small></p>
                        </div>
                    </div>
                    
                    {f"<p><strong>Cover Letter:</strong> {app['cover_letter'][:100]}...</p>" if app['cover_letter'] else ""}
                    {f"<p><strong>Employer Notes:</strong> {app['employer_notes']}</p>" if app['employer_notes'] else ""}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("You haven't applied to any jobs yet. Start browsing jobs to apply!")

def show_user_profile():
    """User profile management"""
    st.markdown("### 👤 My Profile")
    
    tab1, tab2, tab3 = st.tabs(["Basic Info", "Skills & Experience", "Preferences"])
    
    with tab1:
        st.markdown("#### Basic Information")
        
        col1, col2 = st.columns(2)
        with col1:
            full_name = st.text_input("Full Name", value=st.session_state.user_data['full_name'])
            email = st.text_input("Email", value=st.session_state.user_data['email'], disabled=True)
            phone = st.text_input("Phone", value=st.session_state.user_data.get('phone', ''))
        
        with col2:
            location = st.text_input("Location", placeholder="e.g., Bangalore, Karnataka")
            current_position = st.text_input("Current Position", placeholder="e.g., Software Developer")
            experience_years = st.number_input("Years of Experience", min_value=0, max_value=50, value=0)
        
        bio = st.text_area("Bio", placeholder="Tell us about yourself...", height=100)
        
        if st.button("Update Basic Info", type="primary"):
            st.success("Profile updated successfully!")
    
    with tab2:
        st.markdown("#### Skills & Experience")
        
        col1, col2 = st.columns(2)
        with col1:
            education_level = st.selectbox("Education Level", 
                                         ["High School", "Diploma", "Bachelor's", "Master's", "PhD"])
            skills = st.text_area("Skills (comma-separated)", 
                                placeholder="e.g., Python, Teaching, Communication")
        
        with col2:
            languages = st.text_area("Languages (comma-separated)", 
                                   placeholder="e.g., English, Hindi, Kannada")
            portfolio_url = st.text_input("Portfolio URL", placeholder="https://yourportfolio.com")
        
        linkedin_url = st.text_input("LinkedIn Profile", placeholder="https://linkedin.com/in/yourprofile")
        github_url = st.text_input("GitHub Profile", placeholder="https://github.com/yourusername")
        
        # Video resume upload
        st.markdown("#### 🎥 Video Resume")
        st.info("Upload a 2-3 minute video introducing yourself (coming soon)")
        
        # Resume upload
        st.markdown("#### 📄 Resume Upload")
        uploaded_file = st.file_uploader("Upload your resume", type=['pdf', 'doc', 'docx'])
        
        if st.button("Update Skills & Experience", type="primary"):
            st.success("Skills and experience updated successfully!")
    
    with tab3:
        st.markdown("#### Job Preferences")
        
        col1, col2 = st.columns(2)
        with col1:
            preferred_job_types = st.multiselect("Preferred Job Types", 
                                               ["Full-time", "Part-time", "Contract", "Internship", "Remote"])
            salary_expectation = st.text_input("Salary Expectation", placeholder="e.g., 5-8 LPA")
        
        with col2:
            preferred_locations = st.text_area("Preferred Locations", 
                                             placeholder="e.g., Bangalore, Mumbai, Remote")
            availability = st.selectbox("Availability", 
                                      ["Immediate", "2 weeks", "1 month", "2 months", "3+ months"])
        
        if st.button("Update Preferences", type="primary"):
            st.success("Preferences updated successfully!")

def show_messages():
    """Real-time messaging system"""
    st.markdown("### 💬 Messages")
    
    st.info("Real-time messaging with employers will be available soon!")
    
    # Mock conversation
    st.markdown("#### Recent Conversations")
    
    conversations = [
        {"company": "ABC School", "last_message": "We'd like to schedule an interview", "time": "2 hours ago"},
        {"company": "XYZ Tech", "last_message": "Thank you for your application", "time": "1 day ago"},
    ]
    
    for conv in conversations:
        with st.container():
            st.markdown(f"""
            <div class="job-card">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <h5>{conv['company']}</h5>
                        <p>{conv['last_message']}</p>
                    </div>
                    <div>
                        <small>{conv['time']}</small>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_employer_dashboard():
    """Employer dashboard"""
    with st.sidebar:
        st.markdown(f"### Welcome, {st.session_state.user_data['company_name']}!")
        
        selected = option_menu(
            menu_title="Navigation",
            options=["🏠 Dashboard", "📝 Post Jobs", "👥 Candidates", "📊 Analytics", "⚙️ Settings"],
            icons=["house", "plus-circle", "people", "graph-up", "gear"],
            menu_icon="building",
            default_index=0,
        )
        
        if st.button("Logout", type="secondary"):
            st.session_state.logged_in = False
            st.session_state.user_type = None
            st.session_state.user_data = None
            st.rerun()
    
    if selected == "🏠 Dashboard":
        show_employer_home()
    elif selected == "📝 Post Jobs":
        show_post_job()
    elif selected == "👥 Candidates":
        show_candidates()
    elif selected == "📊 Analytics":
        show_employer_analytics()
    elif selected == "⚙️ Settings":
        show_employer_settings()

def show_employer_home():
    """Employer home dashboard"""
    st.markdown("### 🏠 Employer Dashboard")
    
    # Quick stats
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stats-card">
            <h3>5</h3>
            <p>Active Jobs</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stats-card">
            <h3>23</h3>
            <p>Applications</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stats-card">
            <h3>8</h3>
            <p>Shortlisted</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stats-card">
            <h3>2</h3>
            <p>Hired</p>
        </div>
        """, unsafe_allow_html=True)

def show_post_job():
    """Post a new job"""
    st.markdown("### 📝 Post a New Job")
    
    with st.form("post_job_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Job Title*", placeholder="e.g., Mathematics Teacher")
            location = st.text_input("Location*", placeholder="e.g., Bangalore, Karnataka")
            job_type = st.selectbox("Job Type*", ["Full-time", "Part-time", "Contract", "Internship"])
            experience_level = st.selectbox("Experience Level", ["Fresher", "1-3 years", "3-5 years", "5+ years"])
        
        with col2:
            category = st.selectbox("Category*", ["Teaching", "Administrative", "Technical", "Research", "Other"])
            salary_range = st.text_input("Salary Range*", placeholder="e.g., 3-5 LPA")
            application_deadline = st.date_input("Application Deadline")
            skills_required = st.text_area("Required Skills (comma-separated)", 
                                         placeholder="e.g., Mathematics, Classroom Management")
        
        description = st.text_area("Job Description*", height=150, 
                                 placeholder="Describe the role, responsibilities, and requirements...")
        requirements = st.text_area("Additional Requirements", height=100)
        benefits = st.text_area("Benefits & Perks", height=100)
        
        submitted = st.form_submit_button("Post Job", type="primary")
        
        if submitted:
            if title and location and job_type and description and salary_range:
                employer_id = st.session_state.user_data['id']
                skills_list = [skill.strip() for skill in skills_required.split(',') if skill.strip()]
                
                job_id = db.create_job(
                    employer_id=employer_id,
                    title=title,
                    description=description,
                    location=location,
                    job_type=job_type.lower(),
                    salary_range=salary_range,
                    skills_required=skills_list,
                    requirements=requirements,
                    category=category.lower(),
                    application_deadline=str(application_deadline) if application_deadline else None
                )
                
                st.success(f"Job posted successfully! Job ID: {job_id}")
            else:
                st.error("Please fill in all required fields!")

def show_candidates():
    """Show candidate recommendations"""
    st.markdown("### 👥 Candidate Pool")
    
    st.info("AI-powered candidate recommendations will be shown here based on your job postings.")

def show_employer_analytics():
    """Employer analytics dashboard"""
    st.markdown("### 📊 Hiring Analytics")
    
    # Mock data for demo
    data = {
        'Month': ['Jan', 'Feb', 'Mar', 'Apr', 'May'],
        'Applications': [15, 23, 18, 31, 28],
        'Interviews': [5, 8, 6, 12, 10],
        'Hired': [1, 2, 1, 3, 2]
    }
    
    df = pd.DataFrame(data)
    
    fig = px.line(df, x='Month', y=['Applications', 'Interviews', 'Hired'], 
                  title="Hiring Funnel Trends")
    st.plotly_chart(fig, use_container_width=True)

def show_employer_settings():
    """Employer settings"""
    st.markdown("### ⚙️ Company Settings")
    
    st.info("Company profile and settings management coming soon!")

def show_institution_dashboard():
    """Institution dashboard for placement management"""
    st.markdown("### 🏫 Institution Dashboard")
    st.info("Institution placement management system coming soon!")

def apply_for_job(job):
    """Apply for a job"""
    st.markdown(f"### Apply for: {job['title']}")
    
    with st.form("apply_form"):
        cover_letter = st.text_area("Cover Letter", height=150,
                                  placeholder="Why are you interested in this position?")
        
        submitted = st.form_submit_button("Submit Application", type="primary")
        
        if submitted:
            user_id = st.session_state.user_data['id']
            success = db.apply_for_job(job['id'], user_id, cover_letter)
            
            if success:
                st.success("Application submitted successfully!")
            else:
                st.error("You have already applied for this job or an error occurred.")

def show_job_details(job):
    """Show detailed job information"""
    st.markdown(f"### {job['title']}")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f"**Company:** {job['company_name']}")
        st.markdown(f"**Location:** {job['location']}")
        st.markdown(f"**Job Type:** {job['job_type'].title()}")
        st.markdown(f"**Experience Level:** {job['experience_level']}")
        st.markdown(f"**Salary:** {job['salary_range']}")
        
        st.markdown("#### Job Description")
        st.markdown(job['description'])
        
        if job['requirements']:
            st.markdown("#### Requirements")
            st.markdown(job['requirements'])
    
    with col2:
        st.markdown("#### Required Skills")
        for skill in job['skills_required']:
            st.markdown(f"• {skill}")
        
        st.markdown("#### Job Stats")
        st.metric("Applications", job['application_count'])
        st.metric("Views", job['view_count'])
        
        if st.button("Apply Now", type="primary", use_container_width=True):
            apply_for_job(job)

if __name__ == "__main__":
    main()