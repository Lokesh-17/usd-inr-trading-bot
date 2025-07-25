import sqlite3
import json
import uuid
import datetime
import hashlib
from typing import List, Dict

def hash_password(password: str) -> str:
    """Hash password for secure storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def seed_database():
    """Populate database with sample data for demonstration"""
    
    conn = sqlite3.connect('educareer_plus.db')
    cursor = conn.cursor()
    
    print("🌱 Seeding EduCareer+ database with sample data...")
    
    # Sample users data
    sample_users = [
        # Job Seekers
        {
            'name': 'Priya Sharma',
            'email': 'priya.sharma@email.com',
            'password': 'password123',
            'user_type': 'job_seeker',
            'profile_data': {
                'skills': ['Python', 'Data Analysis', 'Machine Learning', 'SQL'],
                'experience_years': 3,
                'preferred_location': 'Bangalore',
                'job_type': 'full_time',
                'bio': 'Passionate data scientist with 3 years of experience in machine learning and analytics.'
            },
            'is_verified': True
        },
        {
            'name': 'Rahul Kumar',
            'email': 'rahul.kumar@email.com', 
            'password': 'password123',
            'user_type': 'job_seeker',
            'profile_data': {
                'skills': ['Java', 'Spring Boot', 'Microservices', 'AWS'],
                'experience_years': 5,
                'preferred_location': 'Mumbai',
                'job_type': 'full_time',
                'bio': 'Senior Java developer with expertise in microservices architecture and cloud technologies.'
            },
            'is_verified': True
        },
        {
            'name': 'Anita Verma',
            'email': 'anita.verma@email.com',
            'password': 'password123',
            'user_type': 'job_seeker',
            'profile_data': {
                'skills': ['Teaching', 'Communication', 'Curriculum Development', 'Leadership'],
                'experience_years': 8,
                'preferred_location': 'Delhi',
                'job_type': 'full_time',
                'bio': 'Experienced educator with 8 years in curriculum development and student mentoring.'
            },
            'is_verified': True
        },
        {
            'name': 'Vikash Singh',
            'email': 'vikash.singh@email.com',
            'password': 'password123',
            'user_type': 'job_seeker',
            'profile_data': {
                'skills': ['React', 'JavaScript', 'Node.js', 'MongoDB'],
                'experience_years': 2,
                'preferred_location': 'Pune',
                'job_type': 'full_time',
                'bio': 'Frontend developer passionate about creating user-friendly web applications.'
            },
            'is_verified': False
        },
        
        # Employers
        {
            'name': 'TechCorp Solutions',
            'email': 'hr@techcorp.com',
            'password': 'password123',
            'user_type': 'employer',
            'profile_data': {
                'company_name': 'TechCorp Solutions',
                'industry': 'Technology',
                'company_size': '201-1000'
            },
            'is_verified': True
        },
        {
            'name': 'EduLearn Institute',
            'email': 'careers@edulearn.com',
            'password': 'password123',
            'user_type': 'employer',
            'profile_data': {
                'company_name': 'EduLearn Institute',
                'industry': 'Education',
                'company_size': '51-200'
            },
            'is_verified': True
        },
        {
            'name': 'DataViz Analytics',
            'email': 'hiring@dataviz.com',
            'password': 'password123',
            'user_type': 'employer',
            'profile_data': {
                'company_name': 'DataViz Analytics',
                'industry': 'Technology',
                'company_size': '11-50'
            },
            'is_verified': True
        },
        
        # Educational Institutions
        {
            'name': 'St. Mary\'s College',
            'email': 'placement@stmarys.edu',
            'password': 'password123',
            'user_type': 'institution',
            'profile_data': {
                'institution_name': 'St. Mary\'s College',
                'institution_type': 'College',
                'accreditation': 'NAAC A+'
            },
            'is_verified': True
        }
    ]
    
    # Insert users
    user_ids = {}
    for user in sample_users:
        user_id = str(uuid.uuid4())
        user_ids[user['email']] = user_id
        
        cursor.execute('''
            INSERT INTO users (id, name, email, password_hash, user_type, profile_data, created_at, is_verified)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_id,
            user['name'],
            user['email'],
            hash_password(user['password']),
            user['user_type'],
            json.dumps(user['profile_data']),
            datetime.datetime.now(),
            user['is_verified']
        ))
    
    print(f"✅ Inserted {len(sample_users)} users")
    
    # Sample jobs data
    sample_jobs = [
        {
            'employer_email': 'hr@techcorp.com',
            'title': 'Senior Python Developer',
            'description': '''We are looking for a Senior Python Developer to join our growing team. You will be responsible for developing high-quality applications, collaborating with cross-functional teams, and mentoring junior developers.

Key Responsibilities:
• Design and develop scalable Python applications
• Work with data science teams on ML pipelines
• Code review and mentoring
• Participate in architectural decisions

Requirements:
• 3+ years of Python development experience
• Strong knowledge of Django/Flask frameworks
• Experience with databases (PostgreSQL, MongoDB)
• Familiarity with cloud platforms (AWS/GCP)''',
            'requirements': [
                '3+ years Python experience',
                'Django/Flask expertise',
                'Database knowledge',
                'Cloud platform experience'
            ],
            'location': 'Bangalore, Karnataka',
            'salary_range': '12-18 LPA',
            'job_type': 'full_time',
            'category': 'technology',
            'skills_required': ['Python', 'Django', 'PostgreSQL', 'AWS', 'Machine Learning'],
            'is_verified': True,
            'expires_days': 30
        },
        {
            'employer_email': 'hr@techcorp.com',
            'title': 'Full Stack Java Developer',
            'description': '''Join our dynamic development team as a Full Stack Java Developer. You'll work on cutting-edge projects using modern Java technologies and frameworks.

Key Responsibilities:
• Develop and maintain Java-based applications
• Build responsive user interfaces
• Integrate with RESTful APIs and microservices
• Collaborate with DevOps for deployment

Requirements:
• 4+ years of Java development experience
• Proficiency in Spring Boot and Spring Framework
• Frontend experience with React or Angular
• Knowledge of microservices architecture''',
            'requirements': [
                '4+ years Java experience',
                'Spring Boot expertise',
                'Frontend framework knowledge',
                'Microservices experience'
            ],
            'location': 'Mumbai, Maharashtra',
            'salary_range': '15-22 LPA',
            'job_type': 'full_time',
            'category': 'technology',
            'skills_required': ['Java', 'Spring Boot', 'React', 'Microservices', 'AWS'],
            'is_verified': True,
            'expires_days': 25
        },
        {
            'employer_email': 'careers@edulearn.com',
            'title': 'Senior Mathematics Teacher',
            'description': '''We are seeking a passionate and experienced Mathematics Teacher to join our academic team. The ideal candidate will have a strong background in mathematics education and a commitment to student success.

Key Responsibilities:
• Plan and deliver engaging mathematics lessons
• Assess student progress and provide feedback
• Develop curriculum materials and resources
• Participate in parent-teacher conferences

Requirements:
• Bachelor's degree in Mathematics or related field
• Teaching certification/B.Ed
• 5+ years of teaching experience
• Strong communication and interpersonal skills''',
            'requirements': [
                'Mathematics degree',
                'Teaching certification',
                '5+ years teaching experience',
                'Strong communication skills'
            ],
            'location': 'Delhi, NCR',
            'salary_range': '8-12 LPA',
            'job_type': 'full_time',
            'category': 'education',
            'skills_required': ['Teaching', 'Mathematics', 'Communication', 'Curriculum Development'],
            'is_verified': True,
            'expires_days': 20
        },
        {
            'employer_email': 'hiring@dataviz.com',
            'title': 'Data Scientist',
            'description': '''We are looking for a Data Scientist to analyze large amounts of raw information to find patterns that will help improve our company. We will rely on you to build data products to extract valuable business insights.

Key Responsibilities:
• Collect and analyze large datasets
• Build predictive models and machine learning algorithms
• Create data visualizations and reports
• Collaborate with business stakeholders

Requirements:
• Master's degree in Data Science, Statistics, or related field
• 2+ years of experience in data science
• Proficiency in Python, R, and SQL
• Experience with machine learning frameworks''',
            'requirements': [
                'Data Science degree',
                '2+ years experience',
                'Python/R/SQL proficiency',
                'ML framework experience'
            ],
            'location': 'Bangalore, Karnataka',
            'salary_range': '10-16 LPA',
            'job_type': 'full_time',
            'category': 'technology',
            'skills_required': ['Python', 'Data Analysis', 'Machine Learning', 'SQL', 'Statistics'],
            'is_verified': True,
            'expires_days': 35
        },
        {
            'employer_email': 'hr@techcorp.com',
            'title': 'Frontend Developer Intern',
            'description': '''Great opportunity for students and fresh graduates to gain hands-on experience in frontend development. You will work with our experienced team on real projects.

Key Responsibilities:
• Develop user-friendly web interfaces
• Learn modern frontend frameworks
• Participate in code reviews
• Contribute to team projects

Requirements:
• Currently pursuing or recently completed degree in Computer Science
• Basic knowledge of HTML, CSS, JavaScript
• Familiarity with React or Vue.js
• Eagerness to learn and grow''',
            'requirements': [
                'Computer Science background',
                'HTML/CSS/JavaScript knowledge',
                'React/Vue.js familiarity',
                'Learning mindset'
            ],
            'location': 'Pune, Maharashtra',
            'salary_range': '2-4 LPA',
            'job_type': 'internship',
            'category': 'technology',
            'skills_required': ['JavaScript', 'React', 'HTML', 'CSS'],
            'is_verified': True,
            'expires_days': 15
        },
        {
            'employer_email': 'careers@edulearn.com',
            'title': 'English Teacher',
            'description': '''We are looking for an enthusiastic English Teacher to foster and facilitate the intellectual and social development of our students.

Key Responsibilities:
• Teach English language and literature
• Develop lesson plans and educational content
• Evaluate student performance
• Maintain classroom discipline

Requirements:
• Bachelor's degree in English or Literature
• Teaching certification
• 2+ years of teaching experience
• Excellent written and verbal communication skills''',
            'requirements': [
                'English/Literature degree',
                'Teaching certification',
                '2+ years experience',
                'Excellent communication'
            ],
            'location': 'Chennai, Tamil Nadu',
            'salary_range': '6-10 LPA',
            'job_type': 'full_time',
            'category': 'education',
            'skills_required': ['Teaching', 'English', 'Communication', 'Literature'],
            'is_verified': True,
            'expires_days': 40
        }
    ]
    
    # Insert jobs
    job_ids = {}
    for job in sample_jobs:
        job_id = str(uuid.uuid4())
        employer_id = user_ids[job['employer_email']]
        
        posted_date = datetime.datetime.now()
        expires_date = posted_date + datetime.timedelta(days=job['expires_days'])
        
        cursor.execute('''
            INSERT INTO jobs (id, employer_id, title, description, requirements, location, salary_range, 
                             job_type, category, skills_required, is_verified, posted_date, expires_date, is_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            job_id,
            employer_id,
            job['title'],
            job['description'],
            json.dumps(job['requirements']),
            job['location'],
            job['salary_range'],
            job['job_type'],
            job['category'],
            json.dumps(job['skills_required']),
            job['is_verified'],
            posted_date,
            expires_date,
            True
        ))
        
        job_ids[job['title']] = job_id
    
    print(f"✅ Inserted {len(sample_jobs)} jobs")
    
    # Sample applications
    sample_applications = [
        {
            'job_title': 'Senior Python Developer',
            'applicant_email': 'priya.sharma@email.com',
            'status': 'shortlisted',
            'cover_letter': '''Dear Hiring Manager,

I am excited to apply for the Senior Python Developer position at TechCorp Solutions. With 3 years of experience in Python development and a strong background in data science, I believe I would be a valuable addition to your team.

In my current role, I have:
• Developed scalable Python applications using Django
• Built machine learning pipelines for data analysis
• Mentored junior developers and conducted code reviews
• Worked extensively with PostgreSQL and AWS services

I am particularly drawn to TechCorp's innovative approach to technology solutions and would love the opportunity to contribute to your team's success.

Thank you for considering my application.

Best regards,
Priya Sharma''',
            'days_ago': 5
        },
        {
            'job_title': 'Full Stack Java Developer',
            'applicant_email': 'rahul.kumar@email.com',
            'status': 'reviewing',
            'cover_letter': '''Dear TechCorp Team,

I am writing to express my interest in the Full Stack Java Developer position. With 5 years of Java development experience and expertise in Spring Boot and microservices, I am confident I can contribute effectively to your development team.

My experience includes:
• Building enterprise applications with Spring Boot
• Developing microservices architectures
• Frontend development with React
• Cloud deployment on AWS

I am excited about the opportunity to work on cutting-edge projects and collaborate with your talented team.

Looking forward to hearing from you.

Best regards,
Rahul Kumar''',
            'days_ago': 3
        },
        {
            'job_title': 'Senior Mathematics Teacher',
            'applicant_email': 'anita.verma@email.com',
            'status': 'applied',
            'cover_letter': '''Dear EduLearn Institute,

I am thrilled to apply for the Senior Mathematics Teacher position. With 8 years of teaching experience and a passion for mathematics education, I am eager to contribute to your institution's academic excellence.

My qualifications include:
• Bachelor's degree in Mathematics with B.Ed certification
• 8 years of teaching experience across different grade levels
• Curriculum development and assessment expertise
• Strong track record of student achievement

I believe in making mathematics accessible and engaging for all students, and I would be honored to join your academic team.

Sincerely,
Anita Verma''',
            'days_ago': 7
        },
        {
            'job_title': 'Data Scientist',
            'applicant_email': 'priya.sharma@email.com',
            'status': 'applied',
            'cover_letter': '''Dear DataViz Analytics Team,

I am interested in the Data Scientist position at your company. My background in data analysis and machine learning aligns well with your requirements.

Key highlights of my experience:
• 3 years of experience in data science and analytics
• Proficiency in Python, SQL, and machine learning frameworks
• Experience with data visualization tools
• Strong statistical analysis skills

I am excited about the opportunity to work with your team on challenging data problems.

Best regards,
Priya Sharma''',
            'days_ago': 2
        },
        {
            'job_title': 'Frontend Developer Intern',
            'applicant_email': 'vikash.singh@email.com',
            'status': 'applied',
            'cover_letter': '''Dear TechCorp Hiring Team,

I am excited to apply for the Frontend Developer Intern position. As a recent graduate with 2 years of experience in web development, I am eager to learn and contribute to your team.

My skills include:
• Proficiency in React, JavaScript, HTML, and CSS
• Experience building responsive web applications
• Understanding of modern development practices
• Enthusiasm for learning new technologies

I would be grateful for the opportunity to grow my skills while contributing to your projects.

Thank you for your consideration.

Best regards,
Vikash Singh''',
            'days_ago': 1
        }
    ]
    
    # Insert applications
    for app in sample_applications:
        application_id = str(uuid.uuid4())
        job_id = job_ids[app['job_title']]
        applicant_id = user_ids[app['applicant_email']]
        
        applied_date = datetime.datetime.now() - datetime.timedelta(days=app['days_ago'])
        
        cursor.execute('''
            INSERT INTO applications (id, job_id, applicant_id, status, applied_date, cover_letter, resume_path, video_intro_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            application_id,
            job_id,
            applicant_id,
            app['status'],
            applied_date,
            app['cover_letter'],
            f"resumes/{application_id}_resume.pdf",
            None
        ))
    
    print(f"✅ Inserted {len(sample_applications)} applications")
    
    # Sample skill assessments
    sample_assessments = [
        {
            'user_email': 'priya.sharma@email.com',
            'skill_name': 'Python Programming',
            'score': 92,
            'days_ago': 10
        },
        {
            'user_email': 'priya.sharma@email.com',
            'skill_name': 'Data Analysis',
            'score': 88,
            'days_ago': 8
        },
        {
            'user_email': 'rahul.kumar@email.com',
            'skill_name': 'Java Programming',
            'score': 95,
            'days_ago': 15
        },
        {
            'user_email': 'anita.verma@email.com',
            'skill_name': 'Communication Skills',
            'score': 96,
            'days_ago': 12
        },
        {
            'user_email': 'anita.verma@email.com',
            'skill_name': 'Teaching Methodology',
            'score': 94,
            'days_ago': 5
        },
        {
            'user_email': 'vikash.singh@email.com',
            'skill_name': 'JavaScript Programming',
            'score': 78,
            'days_ago': 3
        }
    ]
    
    # Insert skill assessments
    for assessment in sample_assessments:
        assessment_id = str(uuid.uuid4())
        user_id = user_ids[assessment['user_email']]
        assessment_date = datetime.datetime.now() - datetime.timedelta(days=assessment['days_ago'])
        
        cursor.execute('''
            INSERT INTO skill_assessments (id, user_id, skill_name, score, assessment_date, certificate_path)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            assessment_id,
            user_id,
            assessment['skill_name'],
            assessment['score'],
            assessment_date,
            f"certificates/{assessment_id}_{assessment['skill_name'].replace(' ', '_')}.pdf"
        ))
    
    print(f"✅ Inserted {len(sample_assessments)} skill assessments")
    
    # Sample messages
    sample_messages = [
        {
            'sender_email': 'hr@techcorp.com',
            'receiver_email': 'priya.sharma@email.com',
            'message': 'Hi Priya, Thank you for your application for the Senior Python Developer position. We were impressed with your profile and would like to schedule an interview. Are you available for a call this week?',
            'hours_ago': 2
        },
        {
            'sender_email': 'priya.sharma@email.com',
            'receiver_email': 'hr@techcorp.com',
            'message': 'Hello! Thank you for reaching out. I am very excited about this opportunity and would be happy to schedule an interview. I am available Monday through Thursday this week between 10 AM and 4 PM. Please let me know what works best for you.',
            'hours_ago': 1
        },
        {
            'sender_email': 'careers@edulearn.com',
            'receiver_email': 'anita.verma@email.com',
            'message': 'Dear Anita, We have received your application for the Mathematics Teacher position. Your experience looks very promising. Could you please send us your teaching portfolio and references?',
            'hours_ago': 24
        }
    ]
    
    # Insert messages
    for msg in sample_messages:
        message_id = str(uuid.uuid4())
        sender_id = user_ids[msg['sender_email']]
        receiver_id = user_ids[msg['receiver_email']]
        timestamp = datetime.datetime.now() - datetime.timedelta(hours=msg['hours_ago'])
        
        cursor.execute('''
            INSERT INTO messages (id, sender_id, receiver_id, job_id, message, timestamp, is_read)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            message_id,
            sender_id,
            receiver_id,
            None,  # job_id can be null for general messages
            msg['message'],
            timestamp,
            False
        ))
    
    print(f"✅ Inserted {len(sample_messages)} messages")
    
    conn.commit()
    conn.close()
    
    print("\n🎉 Database seeding completed successfully!")
    print("\n📋 Sample Login Credentials:")
    print("=" * 50)
    print("Job Seekers:")
    print("• priya.sharma@email.com / password123 (Verified)")
    print("• rahul.kumar@email.com / password123 (Verified)")
    print("• anita.verma@email.com / password123 (Verified)")
    print("• vikash.singh@email.com / password123")
    print("\nEmployers:")
    print("• hr@techcorp.com / password123 (Verified)")
    print("• careers@edulearn.com / password123 (Verified)")
    print("• hiring@dataviz.com / password123 (Verified)")
    print("\nInstitutions:")
    print("• placement@stmarys.edu / password123 (Verified)")
    print("=" * 50)

if __name__ == "__main__":
    seed_database()