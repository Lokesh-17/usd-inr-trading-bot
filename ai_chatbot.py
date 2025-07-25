import streamlit as st
import json
import datetime
from typing import List, Dict, Optional
import re

class EduCareerChatbot:
    """AI-powered chatbot for EduCareer+ job portal"""
    
    def __init__(self):
        self.conversation_history = []
        self.user_context = {}
        
    def get_response(self, user_message: str, user_data: dict = None) -> str:
        """Generate AI response based on user message and context"""
        
        # Store user context
        if user_data:
            self.user_context = user_data
        
        # Clean and analyze user message
        message_lower = user_message.lower().strip()
        
        # Intent classification
        intent = self.classify_intent(message_lower)
        
        # Generate response based on intent
        response = self.generate_response(intent, message_lower, user_message)
        
        # Store conversation
        self.conversation_history.append({
            'user': user_message,
            'bot': response,
            'timestamp': datetime.datetime.now().isoformat(),
            'intent': intent
        })
        
        return response
    
    def classify_intent(self, message: str) -> str:
        """Classify user intent from message"""
        
        # Job search related
        if any(keyword in message for keyword in ['find job', 'search job', 'looking for', 'job openings', 'vacancies']):
            return 'job_search'
        
        # Application related
        if any(keyword in message for keyword in ['apply', 'application', 'resume', 'cv']):
            return 'application_help'
        
        # Skill assessment
        if any(keyword in message for keyword in ['skill', 'test', 'assessment', 'certification']):
            return 'skill_assessment'
        
        # Profile help
        if any(keyword in message for keyword in ['profile', 'update profile', 'edit profile']):
            return 'profile_help'
        
        # Salary/compensation
        if any(keyword in message for keyword in ['salary', 'pay', 'compensation', 'benefits']):
            return 'salary_info'
        
        # Interview preparation
        if any(keyword in message for keyword in ['interview', 'preparation', 'tips']):
            return 'interview_help'
        
        # Company information
        if any(keyword in message for keyword in ['company', 'employer', 'organization']):
            return 'company_info'
        
        # General greeting
        if any(keyword in message for keyword in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            return 'greeting'
        
        # Help/support
        if any(keyword in message for keyword in ['help', 'support', 'how to', 'guide']):
            return 'help'
        
        return 'general'
    
    def generate_response(self, intent: str, message_lower: str, original_message: str) -> str:
        """Generate appropriate response based on intent"""
        
        user_name = self.user_context.get('name', 'there')
        user_type = self.user_context.get('user_type', 'user')
        
        if intent == 'greeting':
            return f"Hello {user_name}! 👋 Welcome to EduCareer+. I'm here to help you with your job search journey. How can I assist you today?"
        
        elif intent == 'job_search':
            if user_type == 'job_seeker':
                profile_data = self.user_context.get('profile_data', {})
                skills = profile_data.get('skills', [])
                location = profile_data.get('preferred_location', '')
                
                response = f"I'll help you find the perfect job! 🎯\n\n"
                
                if skills:
                    response += f"Based on your skills ({', '.join(skills[:3])}), I recommend:\n"
                    response += "• Use the 'Find Jobs' section with skill-based filters\n"
                    response += "• Check out our AI-powered job recommendations on your dashboard\n"
                    response += "• Consider taking skill assessments to boost your profile\n\n"
                
                if location:
                    response += f"For jobs in {location}, try using location filters in the search.\n\n"
                
                response += "💡 Pro tip: Complete your profile and take skill assessments for better job matches!"
                
                return response
            else:
                return "I can help you find great candidates! Use the 'Candidates' section to browse qualified job seekers, or post a job to attract applications."
        
        elif intent == 'application_help':
            return """Here's how to create a winning job application: 📋

**Resume Tips:**
• Keep it concise (1-2 pages)
• Highlight relevant skills and experience
• Use action verbs and quantify achievements
• Ensure it's ATS-friendly

**Cover Letter:**
• Personalize for each job
• Show enthusiasm and cultural fit
• Highlight specific achievements
• Keep it under 300 words

**Video Introduction:**
• Keep it 30-60 seconds
• Introduce yourself professionally
• Mention key qualifications
• Show your personality

Would you like specific help with any of these areas?"""
        
        elif intent == 'skill_assessment':
            return """Skill assessments are a great way to showcase your expertise! 🎯

**Available Assessments:**
• Python Programming
• Communication Skills
• Data Analysis
• Teaching Methodology

**Benefits:**
• Verified skills get higher visibility
• Improves job matching accuracy
• Shows commitment to professional development
• Builds employer confidence

**Tips for Success:**
• Practice beforehand
• Read questions carefully
• Take your time
• Review basics before starting

Head to the 'Skill Assessment' section to get started!"""
        
        elif intent == 'profile_help':
            return """A complete profile is key to success! 👤

**Essential Elements:**
• Professional profile picture
• Detailed skills list
• Work experience
• Education background
• Bio/summary
• Video introduction (optional but recommended)

**Tips:**
• Use keywords relevant to your field
• Keep information current
• Showcase achievements with numbers
• Add certifications and courses

**For Better Matches:**
• Set location preferences
• Specify job type preferences
• List salary expectations
• Update skills regularly

Visit your 'Profile' section to make updates!"""
        
        elif intent == 'salary_info':
            return """Here's guidance on salary and compensation: 💰

**Research Tips:**
• Use salary comparison websites
• Consider location differences
• Factor in experience level
• Include benefits in total compensation

**Negotiation Advice:**
• Research market rates first
• Highlight your unique value
• Be prepared to justify your ask
• Consider non-salary benefits

**On EduCareer+:**
• Many jobs show salary ranges
• Use filters to find jobs in your range
• Verified employers often provide accurate info

**Remember:** Your skills assessments and experience level impact your earning potential!"""
        
        elif intent == 'interview_help':
            return """Interview preparation made easy! 🎤

**Before the Interview:**
• Research the company thoroughly
• Practice common questions
• Prepare specific examples (STAR method)
• Plan your outfit and route

**Common Questions to Prepare:**
• "Tell me about yourself"
• "Why do you want this job?"
• "What are your strengths/weaknesses?"
• "Where do you see yourself in 5 years?"

**Questions to Ask Them:**
• About company culture
• Growth opportunities
• Day-to-day responsibilities
• Team dynamics

**Virtual Interview Tips:**
• Test your technology beforehand
• Ensure good lighting and background
• Maintain eye contact with camera
• Have backup plans for tech issues

Good luck! 🍀"""
        
        elif intent == 'company_info':
            return """Finding the right company fit is crucial! 🏢

**Research Areas:**
• Company mission and values
• Recent news and developments
• Employee reviews and ratings
• Growth trajectory and stability
• Work culture and benefits

**On EduCareer+:**
• Look for verified company badges
• Check employer profiles
• Read job descriptions carefully
• Use our messaging system to ask questions

**Red Flags to Watch:**
• Vague job descriptions
• Unrealistic salary promises
• Poor communication
• Lack of company information

**Green Flags:**
• Detailed job postings
• Quick response times
• Professional communication
• Clear growth paths

Trust your instincts and do your research!"""
        
        elif intent == 'help':
            return """I'm here to help with all aspects of your job search! 🤝

**What I can help with:**
• Finding and applying to jobs
• Profile optimization
• Skill assessment guidance
• Interview preparation
• Salary negotiation tips
• Company research
• Application tracking

**Platform Features:**
• AI-powered job matching
• Verified job listings
• Skill assessments
• Real-time messaging
• Video introductions
• Application tracking

**Need specific help?** Just ask me:
• "How do I improve my profile?"
• "What jobs match my skills?"
• "How do I prepare for interviews?"
• "Tell me about skill assessments"

What would you like help with today?"""
        
        else:  # general
            return f"""I understand you're looking for assistance, {user_name}! 

I can help you with:
• 🔍 Finding jobs that match your skills
• 📝 Improving your applications
• 🎯 Taking skill assessments
• 💬 Interview preparation
• 👤 Profile optimization
• 💰 Salary guidance

Could you be more specific about what you'd like help with? For example:
• "Help me find Python developer jobs"
• "How do I write a better cover letter?"
• "What should I include in my profile?"

I'm here to make your job search journey smoother!"""

    def get_job_recommendations(self, user_skills: List[str], location: str = "") -> str:
        """Generate job recommendations based on user skills"""
        
        recommendations = []
        
        # Skill-based job suggestions
        skill_jobs = {
            'python': ['Python Developer', 'Data Scientist', 'Backend Developer', 'ML Engineer'],
            'java': ['Java Developer', 'Software Engineer', 'Backend Developer', 'Full Stack Developer'],
            'javascript': ['Frontend Developer', 'Full Stack Developer', 'Web Developer', 'React Developer'],
            'teaching': ['Teacher', 'Instructor', 'Training Specialist', 'Educational Consultant'],
            'data analysis': ['Data Analyst', 'Business Analyst', 'Research Analyst', 'Data Scientist'],
            'communication': ['Content Writer', 'Marketing Specialist', 'Customer Success Manager', 'Sales Representative']
        }
        
        for skill in user_skills:
            skill_lower = skill.lower()
            for key, jobs in skill_jobs.items():
                if key in skill_lower:
                    recommendations.extend(jobs)
        
        if recommendations:
            unique_recommendations = list(set(recommendations))[:5]
            response = f"Based on your skills, here are some job recommendations:\n\n"
            for i, job in enumerate(unique_recommendations, 1):
                response += f"{i}. {job}\n"
            
            response += f"\n💡 Tip: Use these job titles in your search filters for better results!"
            
            if location:
                response += f"\n📍 Don't forget to set your location filter to '{location}' for local opportunities!"
            
            return response
        
        return "Complete your skills profile to get personalized job recommendations!"

    def get_conversation_summary(self) -> Dict:
        """Get summary of conversation for analytics"""
        
        if not self.conversation_history:
            return {}
        
        intents = [conv['intent'] for conv in self.conversation_history]
        intent_counts = {}
        
        for intent in intents:
            intent_counts[intent] = intent_counts.get(intent, 0) + 1
        
        return {
            'total_messages': len(self.conversation_history),
            'intent_distribution': intent_counts,
            'conversation_start': self.conversation_history[0]['timestamp'],
            'conversation_end': self.conversation_history[-1]['timestamp']
        }

def show_chatbot_interface():
    """Display chatbot interface in Streamlit"""
    
    st.title("🤖 EduCareer+ AI Assistant")
    
    # Initialize chatbot in session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = EduCareerChatbot()
    
    # Display conversation history
    if st.session_state.chatbot.conversation_history:
        st.subheader("Conversation")
        
        for conv in st.session_state.chatbot.conversation_history:
            # User message
            st.markdown(f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {conv['user']}
            </div>
            """, unsafe_allow_html=True)
            
            # Bot response
            st.markdown(f"""
            <div class="chat-message bot-message">
                <strong>AI Assistant:</strong> {conv['bot']}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    with st.form("chat_form"):
        user_input = st.text_area("Ask me anything about your job search...", 
                                height=100,
                                placeholder="e.g., How do I find Python developer jobs?")
        
        col1, col2 = st.columns([1, 4])
        
        with col1:
            send_message = st.form_submit_button("Send", type="primary")
        
        with col2:
            if st.form_submit_button("Clear Chat"):
                st.session_state.chatbot = EduCareerChatbot()
                st.rerun()
    
    if send_message and user_input.strip():
        # Get user context if logged in
        user_context = {}
        if hasattr(st.session_state, 'user_data') and st.session_state.user_data:
            user_context = st.session_state.user_data
        
        # Get bot response
        response = st.session_state.chatbot.get_response(user_input, user_context)
        
        # Rerun to show new conversation
        st.rerun()
    
    # Quick action buttons
    st.markdown("---")
    st.subheader("Quick Help")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔍 Find Jobs", use_container_width=True):
            response = st.session_state.chatbot.get_response(
                "Help me find jobs", 
                st.session_state.get('user_data', {})
            )
            st.rerun()
    
    with col2:
        if st.button("📝 Application Tips", use_container_width=True):
            response = st.session_state.chatbot.get_response(
                "How do I write a good application?", 
                st.session_state.get('user_data', {})
            )
            st.rerun()
    
    with col3:
        if st.button("🎯 Skill Assessment", use_container_width=True):
            response = st.session_state.chatbot.get_response(
                "Tell me about skill assessments", 
                st.session_state.get('user_data', {})
            )
            st.rerun()

if __name__ == "__main__":
    show_chatbot_interface()