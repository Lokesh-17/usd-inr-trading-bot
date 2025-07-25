import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import StandardScaler
from typing import List, Dict, Tuple
import re
from datetime import datetime, timedelta

class AIJobMatcher:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.scaler = StandardScaler()
        
    def extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skills from job description or user profile"""
        # Common skills database (can be expanded)
        common_skills = [
            'python', 'java', 'javascript', 'react', 'node.js', 'sql', 'mongodb',
            'machine learning', 'data science', 'artificial intelligence', 'deep learning',
            'teaching', 'communication', 'leadership', 'project management', 'teamwork',
            'mathematics', 'physics', 'chemistry', 'biology', 'english', 'hindi',
            'classroom management', 'curriculum development', 'lesson planning',
            'microsoft office', 'excel', 'powerpoint', 'google workspace',
            'research', 'writing', 'presentation', 'problem solving', 'critical thinking',
            'html', 'css', 'bootstrap', 'tailwind', 'django', 'flask', 'fastapi',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp', 'git', 'github',
            'photoshop', 'illustrator', 'figma', 'canva', 'video editing',
            'accounting', 'finance', 'marketing', 'sales', 'customer service',
            'content writing', 'social media', 'digital marketing', 'seo'
        ]
        
        text_lower = text.lower()
        found_skills = []
        
        for skill in common_skills:
            if skill.lower() in text_lower:
                found_skills.append(skill)
        
        return found_skills
    
    def calculate_skill_match_score(self, user_skills: List[str], job_skills: List[str]) -> float:
        """Calculate skill match score between user and job"""
        if not user_skills or not job_skills:
            return 0.0
        
        user_skills_lower = [skill.lower() for skill in user_skills]
        job_skills_lower = [skill.lower() for skill in job_skills]
        
        matched_skills = set(user_skills_lower).intersection(set(job_skills_lower))
        
        if not job_skills_lower:
            return 0.0
        
        return len(matched_skills) / len(job_skills_lower)
    
    def calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity using TF-IDF and cosine similarity"""
        try:
            texts = [text1, text2]
            tfidf_matrix = self.vectorizer.fit_transform(texts)
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            return similarity
        except:
            return 0.0
    
    def calculate_location_match(self, user_location: str, job_location: str) -> float:
        """Calculate location match score"""
        if not user_location or not job_location:
            return 0.5  # Neutral score for missing location
        
        user_loc = user_location.lower().strip()
        job_loc = job_location.lower().strip()
        
        # Exact match
        if user_loc == job_loc:
            return 1.0
        
        # City match (extract city names)
        user_words = set(user_loc.split())
        job_words = set(job_loc.split())
        
        common_words = user_words.intersection(job_words)
        if common_words:
            return 0.8
        
        # Remote work keywords
        remote_keywords = ['remote', 'work from home', 'anywhere', 'online']
        if any(keyword in job_loc for keyword in remote_keywords):
            return 0.9
        
        return 0.2  # Different locations
    
    def calculate_experience_match(self, user_experience: int, job_experience_level: str) -> float:
        """Calculate experience level match"""
        if not job_experience_level:
            return 0.7  # Neutral score
        
        job_exp_lower = job_experience_level.lower()
        
        if 'fresher' in job_exp_lower or 'entry' in job_exp_lower:
            if user_experience <= 1:
                return 1.0
            elif user_experience <= 2:
                return 0.8
            else:
                return 0.6
        
        elif '1-3' in job_exp_lower or 'junior' in job_exp_lower:
            if 1 <= user_experience <= 3:
                return 1.0
            elif user_experience <= 5:
                return 0.8
            else:
                return 0.6
        
        elif '3-5' in job_exp_lower or 'mid' in job_exp_lower:
            if 3 <= user_experience <= 5:
                return 1.0
            elif 2 <= user_experience <= 7:
                return 0.8
            else:
                return 0.6
        
        elif '5+' in job_exp_lower or 'senior' in job_exp_lower:
            if user_experience >= 5:
                return 1.0
            elif user_experience >= 3:
                return 0.7
            else:
                return 0.4
        
        return 0.7  # Default neutral score
    
    def calculate_job_type_preference(self, user_preferences: Dict, job_type: str) -> float:
        """Calculate job type preference match"""
        if not user_preferences.get('preferred_job_types'):
            return 0.7  # Neutral if no preference specified
        
        preferred_types = [pref.lower() for pref in user_preferences['preferred_job_types']]
        
        if job_type.lower() in preferred_types:
            return 1.0
        
        # Partial matches
        if 'full-time' in preferred_types and 'full' in job_type.lower():
            return 0.9
        if 'part-time' in preferred_types and 'part' in job_type.lower():
            return 0.9
        if 'remote' in preferred_types and 'remote' in job_type.lower():
            return 0.9
        
        return 0.3
    
    def calculate_salary_match(self, user_expectation: str, job_salary_range: str) -> float:
        """Calculate salary expectation match"""
        if not user_expectation or not job_salary_range:
            return 0.7  # Neutral score
        
        try:
            # Extract numbers from salary strings
            user_nums = re.findall(r'\d+', user_expectation.replace(',', ''))
            job_nums = re.findall(r'\d+', job_salary_range.replace(',', ''))
            
            if not user_nums or not job_nums:
                return 0.7
            
            user_expected = int(user_nums[0]) * (10000 if 'lakh' in user_expectation.lower() else 1000 if 'k' in user_expectation.lower() else 1)
            job_offered = int(job_nums[-1]) * (10000 if 'lakh' in job_salary_range.lower() else 1000 if 'k' in job_salary_range.lower() else 1)
            
            if job_offered >= user_expected:
                return 1.0
            elif job_offered >= user_expected * 0.8:
                return 0.8
            elif job_offered >= user_expected * 0.6:
                return 0.6
            else:
                return 0.3
        except:
            return 0.7
    
    def get_job_recommendations(self, user_profile: Dict, jobs: List[Dict], top_k: int = 10) -> List[Dict]:
        """Get top job recommendations for a user"""
        recommendations = []
        
        user_skills = user_profile.get('skills', [])
        user_location = user_profile.get('location', '')
        user_experience = user_profile.get('experience_years', 0)
        user_bio = user_profile.get('bio', '')
        user_preferences = user_profile.get('preferences', {})
        user_salary_expectation = user_profile.get('salary_expectation', '')
        
        for job in jobs:
            # Calculate various match scores
            skill_score = self.calculate_skill_match_score(user_skills, job.get('skills_required', []))
            location_score = self.calculate_location_match(user_location, job.get('location', ''))
            experience_score = self.calculate_experience_match(user_experience, job.get('experience_level', ''))
            
            # Text similarity between user bio and job description
            text_similarity = self.calculate_text_similarity(user_bio, job.get('description', ''))
            
            # Job type preference
            job_type_score = self.calculate_job_type_preference(user_preferences, job.get('job_type', ''))
            
            # Salary match
            salary_score = self.calculate_salary_match(user_salary_expectation, job.get('salary_range', ''))
            
            # Calculate weighted overall score
            overall_score = (
                skill_score * 0.3 +
                location_score * 0.2 +
                experience_score * 0.2 +
                text_similarity * 0.15 +
                job_type_score * 0.1 +
                salary_score * 0.05
            )
            
            # Boost score for verified employers
            if job.get('employer_verified'):
                overall_score *= 1.1
            
            # Boost score for recent postings
            try:
                job_date = datetime.strptime(job.get('created_at', ''), '%Y-%m-%d %H:%M:%S')
                days_old = (datetime.now() - job_date).days
                if days_old <= 7:
                    overall_score *= 1.05
            except:
                pass
            
            # Generate match reasons
            reasons = []
            if skill_score > 0.5:
                matched_skills = set([s.lower() for s in user_skills]).intersection(
                    set([s.lower() for s in job.get('skills_required', [])])
                )
                reasons.append(f"Strong skill match: {', '.join(list(matched_skills)[:3])}")
            
            if location_score > 0.8:
                reasons.append("Excellent location match")
            elif location_score > 0.5:
                reasons.append("Good location compatibility")
            
            if experience_score > 0.8:
                reasons.append("Perfect experience level match")
            
            if text_similarity > 0.3:
                reasons.append("Profile aligns well with job requirements")
            
            if salary_score > 0.8:
                reasons.append("Salary meets your expectations")
            
            recommendations.append({
                'job': job,
                'match_score': min(overall_score, 1.0),  # Cap at 1.0
                'reasons': reasons,
                'skill_match': skill_score,
                'location_match': location_score,
                'experience_match': experience_score,
                'text_similarity': text_similarity
            })
        
        # Sort by match score and return top_k
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:top_k]
    
    def get_candidate_recommendations(self, job: Dict, candidates: List[Dict], top_k: int = 20) -> List[Dict]:
        """Get top candidate recommendations for a job"""
        recommendations = []
        
        job_skills = job.get('skills_required', [])
        job_location = job.get('location', '')
        job_experience_level = job.get('experience_level', '')
        job_description = job.get('description', '')
        job_type = job.get('job_type', '')
        job_salary = job.get('salary_range', '')
        
        for candidate in candidates:
            candidate_skills = candidate.get('skills', [])
            candidate_location = candidate.get('location', '')
            candidate_experience = candidate.get('experience_years', 0)
            candidate_bio = candidate.get('bio', '')
            candidate_preferences = candidate.get('preferences', {})
            candidate_salary_expectation = candidate.get('salary_expectation', '')
            
            # Calculate match scores
            skill_score = self.calculate_skill_match_score(candidate_skills, job_skills)
            location_score = self.calculate_location_match(candidate_location, job_location)
            experience_score = self.calculate_experience_match(candidate_experience, job_experience_level)
            text_similarity = self.calculate_text_similarity(candidate_bio, job_description)
            job_type_score = self.calculate_job_type_preference(candidate_preferences, job_type)
            salary_score = self.calculate_salary_match(candidate_salary_expectation, job_salary)
            
            # Calculate weighted overall score
            overall_score = (
                skill_score * 0.35 +
                experience_score * 0.25 +
                location_score * 0.15 +
                text_similarity * 0.15 +
                job_type_score * 0.05 +
                salary_score * 0.05
            )
            
            # Boost for verified candidates
            if candidate.get('is_verified'):
                overall_score *= 1.1
            
            # Generate match reasons
            reasons = []
            if skill_score > 0.6:
                reasons.append("Excellent skill match")
            elif skill_score > 0.3:
                reasons.append("Good skill compatibility")
            
            if experience_score > 0.8:
                reasons.append("Perfect experience level")
            
            if location_score > 0.8:
                reasons.append("Local candidate")
            
            recommendations.append({
                'candidate': candidate,
                'match_score': min(overall_score, 1.0),
                'reasons': reasons,
                'skill_match': skill_score,
                'location_match': location_score,
                'experience_match': experience_score
            })
        
        # Sort by match score and return top_k
        recommendations.sort(key=lambda x: x['match_score'], reverse=True)
        return recommendations[:top_k]

class SkillAssessment:
    def __init__(self):
        self.coding_questions = {
            'python': [
                {
                    'question': 'Write a function to find the factorial of a number.',
                    'expected_keywords': ['def', 'factorial', 'return', 'if', 'else'],
                    'difficulty': 'easy',
                    'max_score': 10
                },
                {
                    'question': 'Write a function to check if a string is a palindrome.',
                    'expected_keywords': ['def', 'palindrome', 'return', 'lower', 'reverse'],
                    'difficulty': 'easy',
                    'max_score': 10
                },
                {
                    'question': 'Implement a function to find the second largest number in a list.',
                    'expected_keywords': ['def', 'max', 'sort', 'return', 'list'],
                    'difficulty': 'medium',
                    'max_score': 15
                }
            ],
            'javascript': [
                {
                    'question': 'Write a function to reverse a string.',
                    'expected_keywords': ['function', 'reverse', 'return', 'split', 'join'],
                    'difficulty': 'easy',
                    'max_score': 10
                },
                {
                    'question': 'Create a function that returns the sum of all numbers in an array.',
                    'expected_keywords': ['function', 'sum', 'return', 'reduce', 'forEach'],
                    'difficulty': 'easy',
                    'max_score': 10
                }
            ]
        }
        
        self.communication_questions = [
            {
                'question': 'Describe a challenging project you worked on and how you overcame obstacles.',
                'keywords': ['project', 'challenge', 'overcome', 'solution', 'team', 'problem'],
                'max_score': 20
            },
            {
                'question': 'How would you explain a complex technical concept to a non-technical person?',
                'keywords': ['explain', 'simple', 'example', 'understand', 'analogy'],
                'max_score': 20
            }
        ]
        
        self.teaching_questions = [
            {
                'question': 'How would you handle a disruptive student in your classroom?',
                'keywords': ['student', 'classroom', 'manage', 'behavior', 'positive', 'discipline'],
                'max_score': 25
            },
            {
                'question': 'Describe your approach to lesson planning.',
                'keywords': ['lesson', 'plan', 'objective', 'activity', 'assessment', 'learning'],
                'max_score': 25
            }
        ]
    
    def evaluate_coding_answer(self, skill: str, question_index: int, answer: str) -> Dict:
        """Evaluate a coding answer"""
        if skill not in self.coding_questions:
            return {'score': 0, 'max_score': 0, 'feedback': 'Skill not supported'}
        
        if question_index >= len(self.coding_questions[skill]):
            return {'score': 0, 'max_score': 0, 'feedback': 'Invalid question index'}
        
        question = self.coding_questions[skill][question_index]
        expected_keywords = question['expected_keywords']
        max_score = question['max_score']
        
        answer_lower = answer.lower()
        found_keywords = sum(1 for keyword in expected_keywords if keyword.lower() in answer_lower)
        
        score = int((found_keywords / len(expected_keywords)) * max_score)
        
        feedback = f"Found {found_keywords}/{len(expected_keywords)} expected concepts. "
        if score >= max_score * 0.8:
            feedback += "Excellent solution!"
        elif score >= max_score * 0.6:
            feedback += "Good approach, could be improved."
        else:
            feedback += "Consider reviewing the key concepts."
        
        return {
            'score': score,
            'max_score': max_score,
            'feedback': feedback,
            'keywords_found': found_keywords,
            'total_keywords': len(expected_keywords)
        }
    
    def evaluate_communication_answer(self, question_index: int, answer: str) -> Dict:
        """Evaluate a communication answer"""
        if question_index >= len(self.communication_questions):
            return {'score': 0, 'max_score': 0, 'feedback': 'Invalid question index'}
        
        question = self.communication_questions[question_index]
        keywords = question['keywords']
        max_score = question['max_score']
        
        answer_lower = answer.lower()
        found_keywords = sum(1 for keyword in keywords if keyword.lower() in answer_lower)
        
        # Also consider answer length and structure
        word_count = len(answer.split())
        length_score = min(word_count / 50, 1.0)  # Optimal around 50 words
        
        final_score = int(((found_keywords / len(keywords)) * 0.7 + length_score * 0.3) * max_score)
        
        feedback = f"Answer demonstrates {found_keywords}/{len(keywords)} key concepts. "
        if final_score >= max_score * 0.8:
            feedback += "Excellent communication skills!"
        elif final_score >= max_score * 0.6:
            feedback += "Good communication, could be more detailed."
        else:
            feedback += "Consider providing more specific examples."
        
        return {
            'score': final_score,
            'max_score': max_score,
            'feedback': feedback,
            'keywords_found': found_keywords,
            'word_count': word_count
        }
    
    def evaluate_teaching_answer(self, question_index: int, answer: str) -> Dict:
        """Evaluate a teaching-related answer"""
        if question_index >= len(self.teaching_questions):
            return {'score': 0, 'max_score': 0, 'feedback': 'Invalid question index'}
        
        question = self.teaching_questions[question_index]
        keywords = question['keywords']
        max_score = question['max_score']
        
        answer_lower = answer.lower()
        found_keywords = sum(1 for keyword in keywords if keyword.lower() in answer_lower)
        
        # Consider pedagogical approach
        pedagogical_terms = ['student-centered', 'interactive', 'engaging', 'differentiated', 'inclusive']
        pedagogical_score = sum(1 for term in pedagogical_terms if term in answer_lower) / len(pedagogical_terms)
        
        final_score = int(((found_keywords / len(keywords)) * 0.8 + pedagogical_score * 0.2) * max_score)
        
        feedback = f"Teaching approach shows {found_keywords}/{len(keywords)} key elements. "
        if final_score >= max_score * 0.8:
            feedback += "Excellent teaching methodology!"
        elif final_score >= max_score * 0.6:
            feedback += "Good teaching approach."
        else:
            feedback += "Consider incorporating more student-centered strategies."
        
        return {
            'score': final_score,
            'max_score': max_score,
            'feedback': feedback,
            'keywords_found': found_keywords,
            'pedagogical_score': pedagogical_score
        }