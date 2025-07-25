#!/usr/bin/env python3
"""
EduCareer+ Startup Script
Initializes the database and runs the job portal application
"""

import os
import sys
import subprocess
import sqlite3
from seed_data import seed_database

def check_database_exists():
    """Check if the database file exists"""
    return os.path.exists('educareer_plus.db')

def check_database_populated():
    """Check if the database has sample data"""
    try:
        conn = sqlite3.connect('educareer_plus.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        conn.close()
        return user_count > 0
    except:
        return False

def initialize_database():
    """Initialize the database with sample data"""
    print("🔧 Initializing EduCareer+ database...")
    
    # Import and run the main app to create tables
    from job_portal_app import init_database
    init_database()
    
    # Check if we need to seed data
    if not check_database_populated():
        print("📊 Populating database with sample data...")
        seed_database()
    else:
        print("✅ Database already contains data")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)

def run_application():
    """Run the Streamlit application"""
    print("🚀 Starting EduCareer+ application...")
    print("📱 The application will open in your default browser")
    print("🌐 Access URL: http://localhost:8501")
    print("\n" + "="*60)
    print("🎓 WELCOME TO EDUCAREER+ | SMART JOB PORTAL")
    print("="*60)
    print("\n📋 Sample Login Credentials:")
    print("-" * 30)
    print("Job Seekers:")
    print("• priya.sharma@email.com / password123")
    print("• rahul.kumar@email.com / password123")
    print("• anita.verma@email.com / password123")
    print("• vikash.singh@email.com / password123")
    print("\nEmployers:")
    print("• hr@techcorp.com / password123")
    print("• careers@edulearn.com / password123")
    print("• hiring@dataviz.com / password123")
    print("\nInstitutions:")
    print("• placement@stmarys.edu / password123")
    print("-" * 30)
    print("\n💡 Features to explore:")
    print("• AI-powered job matching")
    print("• Interactive skill assessments")
    print("• Real-time messaging")
    print("• Verified job listings")
    print("• Video profile creation")
    print("• Smart chatbot assistant")
    print("\n🛑 Press Ctrl+C to stop the application")
    print("="*60)
    
    try:
        subprocess.run([sys.executable, "-m", "streamlit", "run", "job_portal_app.py"])
    except KeyboardInterrupt:
        print("\n\n👋 Thank you for using EduCareer+!")
        print("🌟 We hope you enjoyed exploring the future of job portals!")
    except Exception as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

def main():
    """Main function to orchestrate the startup process"""
    print("\n" + "="*60)
    print("🎓 EDUCAREER+ | SMART JOB PORTAL STARTUP")
    print("="*60)
    
    # Check if requirements.txt exists
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt not found!")
        sys.exit(1)
    
    # Install dependencies
    install_dependencies()
    
    # Initialize database if needed
    if not check_database_exists() or not check_database_populated():
        initialize_database()
    else:
        print("✅ Database already initialized")
    
    # Run the application
    run_application()

if __name__ == "__main__":
    main()