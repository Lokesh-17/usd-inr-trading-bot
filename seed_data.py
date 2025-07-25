from database import JobPortalDB
from datetime import datetime, timedelta
import random

def seed_database():
    """Seed the database with sample data"""
    db = JobPortalDB()
    
    print("🌱 Seeding EduCareer+ database...")
    
    # Sample employers
    employers = [
        {
            "email": "hr@abcschool.edu",
            "password": "password123",
            "company_name": "ABC International School",
            "company_type": "school",
            "contact_person": "Priya Sharma"
        },
        {
            "email": "placement@xyztech.com",
            "password": "password123",
            "company_name": "XYZ Tech Solutions",
            "company_type": "company",
            "contact_person": "Rajesh Kumar"
        },
        {
            "email": "admin@defcollege.ac.in",
            "password": "password123",
            "company_name": "DEF Engineering College",
            "company_type": "college",
            "contact_person": "Dr. Anita Rao"
        },
        {
            "email": "hr@greenearth.org",
            "password": "password123",
            "company_name": "Green Earth NGO",
            "company_type": "ngo",
            "contact_person": "Suresh Patel"
        },
        {
            "email": "careers@innovatedu.com",
            "password": "password123",
            "company_name": "InnovateEdu Startup",
            "company_type": "company",
            "contact_person": "Neha Gupta"
        }
    ]
    
    # Create employers
    employer_ids = []
    for emp in employers:
        success = db.create_employer(
            emp["email"], emp["password"], emp["company_name"], 
            emp["company_type"], emp["contact_person"]
        )
        if success:
            # Get employer ID
            employer = db.authenticate_employer(emp["email"], emp["password"])
            if employer:
                employer_ids.append(employer['id'])
                print(f"✅ Created employer: {emp['company_name']}")
    
    # Sample jobs
    jobs = [
        {
            "title": "Mathematics Teacher",
            "description": "We are looking for a passionate Mathematics teacher to join our team. The ideal candidate should have excellent communication skills and experience in teaching high school mathematics.",
            "location": "Bangalore, Karnataka",
            "job_type": "full-time",
            "salary_range": "4-6 LPA",
            "skills_required": ["Mathematics", "Teaching", "Communication", "Classroom Management"],
            "requirements": "B.Ed in Mathematics, 2+ years experience",
            "category": "teaching"
        },
        {
            "title": "Python Developer",
            "description": "Join our dynamic team as a Python Developer. You'll work on exciting projects involving web development, data analysis, and machine learning applications.",
            "location": "Mumbai, Maharashtra",
            "job_type": "full-time",
            "salary_range": "6-10 LPA",
            "skills_required": ["Python", "Django", "SQL", "Git", "Problem Solving"],
            "requirements": "B.Tech/MCA, 1-3 years experience in Python",
            "category": "technical"
        },
        {
            "title": "English Language Instructor",
            "description": "Teach English language and literature to undergraduate students. Create engaging lesson plans and assess student progress.",
            "location": "Chennai, Tamil Nadu",
            "job_type": "full-time",
            "salary_range": "3-5 LPA",
            "skills_required": ["English", "Teaching", "Communication", "Literature"],
            "requirements": "MA in English, B.Ed preferred",
            "category": "teaching"
        },
        {
            "title": "Data Science Intern",
            "description": "Exciting internship opportunity for students interested in data science. Work with real datasets and learn from experienced professionals.",
            "location": "Hyderabad, Telangana",
            "job_type": "internship",
            "salary_range": "15-25K per month",
            "skills_required": ["Python", "Data Science", "Machine Learning", "Statistics"],
            "requirements": "B.Tech/B.Sc final year students",
            "category": "technical"
        },
        {
            "title": "Administrative Assistant",
            "description": "Support the administrative operations of our educational institution. Handle student records, coordinate with faculty, and manage office tasks.",
            "location": "Pune, Maharashtra",
            "job_type": "full-time",
            "salary_range": "2.5-4 LPA",
            "skills_required": ["Microsoft Office", "Communication", "Organization", "Customer Service"],
            "requirements": "Bachelor's degree, 1+ years office experience",
            "category": "administrative"
        },
        {
            "title": "Science Teacher",
            "description": "Teach Physics and Chemistry to high school students. Create interactive lessons and conduct laboratory experiments.",
            "location": "Delhi, NCR",
            "job_type": "full-time",
            "salary_range": "5-7 LPA",
            "skills_required": ["Physics", "Chemistry", "Teaching", "Laboratory Skills"],
            "requirements": "M.Sc in Physics/Chemistry, B.Ed required",
            "category": "teaching"
        },
        {
            "title": "Full Stack Developer",
            "description": "Develop and maintain web applications using modern technologies. Work on both frontend and backend components.",
            "location": "Bangalore, Karnataka",
            "job_type": "full-time",
            "salary_range": "8-12 LPA",
            "skills_required": ["JavaScript", "React", "Node.js", "MongoDB", "HTML", "CSS"],
            "requirements": "B.Tech/MCA, 2-4 years experience",
            "category": "technical"
        },
        {
            "title": "Content Writer",
            "description": "Create engaging educational content for our e-learning platform. Write course materials, blog posts, and marketing content.",
            "location": "Remote",
            "job_type": "part-time",
            "salary_range": "20-30K per month",
            "skills_required": ["Content Writing", "Research", "SEO", "Communication"],
            "requirements": "Bachelor's degree, excellent writing skills",
            "category": "technical"
        },
        {
            "title": "Computer Science Faculty",
            "description": "Teach computer science subjects to engineering students. Conduct research and guide student projects.",
            "location": "Coimbatore, Tamil Nadu",
            "job_type": "full-time",
            "salary_range": "6-9 LPA",
            "skills_required": ["Computer Science", "Programming", "Teaching", "Research"],
            "requirements": "M.Tech/PhD in Computer Science",
            "category": "teaching"
        },
        {
            "title": "Digital Marketing Specialist",
            "description": "Manage digital marketing campaigns for educational institutions. Handle social media, content marketing, and online advertising.",
            "location": "Gurgaon, Haryana",
            "job_type": "full-time",
            "salary_range": "4-7 LPA",
            "skills_required": ["Digital Marketing", "Social Media", "SEO", "Google Ads", "Analytics"],
            "requirements": "Bachelor's degree, 1-3 years experience",
            "category": "technical"
        }
    ]
    
    # Create jobs
    for i, job in enumerate(jobs):
        employer_id = employer_ids[i % len(employer_ids)]  # Distribute jobs among employers
        
        job_id = db.create_job(
            employer_id=employer_id,
            title=job["title"],
            description=job["description"],
            location=job["location"],
            job_type=job["job_type"],
            salary_range=job["salary_range"],
            skills_required=job["skills_required"],
            requirements=job["requirements"],
            category=job["category"]
        )
        print(f"✅ Created job: {job['title']} (ID: {job_id})")
    
    # Sample users (job seekers)
    users = [
        {
            "email": "john.doe@email.com",
            "password": "password123",
            "full_name": "John Doe",
            "phone": "+91-9876543210"
        },
        {
            "email": "priya.singh@email.com",
            "password": "password123",
            "full_name": "Priya Singh",
            "phone": "+91-9876543211"
        },
        {
            "email": "amit.kumar@email.com",
            "password": "password123",
            "full_name": "Amit Kumar",
            "phone": "+91-9876543212"
        },
        {
            "email": "sneha.patel@email.com",
            "password": "password123",
            "full_name": "Sneha Patel",
            "phone": "+91-9876543213"
        },
        {
            "email": "rahul.sharma@email.com",
            "password": "password123",
            "full_name": "Rahul Sharma",
            "phone": "+91-9876543214"
        }
    ]
    
    # Create users
    user_ids = []
    for user in users:
        success = db.create_user(
            user["email"], user["password"], user["full_name"], user["phone"]
        )
        if success:
            # Get user ID
            user_data = db.authenticate_user(user["email"], user["password"])
            if user_data:
                user_ids.append(user_data['id'])
                print(f"✅ Created user: {user['full_name']}")
    
    # Create some sample applications
    if user_ids and employer_ids:
        sample_applications = [
            {"user_idx": 0, "job_idx": 0, "cover_letter": "I am very interested in this Mathematics teaching position and have 3 years of experience."},
            {"user_idx": 1, "job_idx": 1, "cover_letter": "I am a Python developer with strong skills in Django and web development."},
            {"user_idx": 2, "job_idx": 2, "cover_letter": "I have a passion for English literature and teaching experience."},
            {"user_idx": 3, "job_idx": 3, "cover_letter": "I am a final year student eager to learn data science through this internship."},
            {"user_idx": 4, "job_idx": 4, "cover_letter": "I have excellent organizational skills and office management experience."},
        ]
        
        # Get all jobs to apply to
        all_jobs = db.get_jobs(limit=50)
        
        for app in sample_applications:
            if app["user_idx"] < len(user_ids) and app["job_idx"] < len(all_jobs):
                user_id = user_ids[app["user_idx"]]
                job_id = all_jobs[app["job_idx"]]["id"]
                
                success = db.apply_for_job(job_id, user_id, app["cover_letter"])
                if success:
                    print(f"✅ Created application: User {user_id} -> Job {job_id}")
    
    # Create sample skill assessments
    sample_skills = [
        {"user_idx": 0, "skill": "mathematics", "type": "teaching", "score": 18, "max_score": 25},
        {"user_idx": 1, "skill": "python", "type": "coding", "score": 8, "max_score": 10},
        {"user_idx": 2, "skill": "communication", "type": "communication", "score": 16, "max_score": 20},
        {"user_idx": 3, "skill": "python", "type": "coding", "score": 6, "max_score": 10},
        {"user_idx": 4, "skill": "communication", "type": "communication", "score": 14, "max_score": 20},
    ]
    
    for skill in sample_skills:
        if skill["user_idx"] < len(user_ids):
            user_id = user_ids[skill["user_idx"]]
            success = db.save_skill_assessment(
                user_id, skill["skill"], skill["type"], skill["score"], skill["max_score"]
            )
            if success:
                print(f"✅ Created skill assessment: {skill['skill']} for user {user_id}")
    
    print("\n🎉 Database seeding completed successfully!")
    print("\n📝 Sample Login Credentials:")
    print("\n👤 Job Seekers:")
    for user in users[:3]:
        print(f"   Email: {user['email']} | Password: {user['password']}")
    
    print("\n🏢 Employers:")
    for emp in employers[:3]:
        print(f"   Email: {emp['email']} | Password: {emp['password']}")
    
    print(f"\n📊 Summary:")
    print(f"   • {len(employers)} employers created")
    print(f"   • {len(jobs)} jobs posted")
    print(f"   • {len(users)} job seekers registered")
    print(f"   • {len(sample_applications)} applications submitted")
    print(f"   • {len(sample_skills)} skill assessments completed")

if __name__ == "__main__":
    seed_database()