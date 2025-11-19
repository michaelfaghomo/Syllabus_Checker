import re
import PyPDF2
from docx import Document
import os

class SyllabusChecker:
    def __init__(self):
        self.requirements = {
            'course_info': {
                'name': 'Course prefix and number, section number, and title',
                'keywords': [r'\b[A-Z]{2,4}\s*\d{3,4}', r'section\s*\d+', r'course\s*title'],
                'patterns': [r'\b[A-Z]{2,4}\s*-?\s*\d{3,4}', r'section\s*:?\s*\d+']
            },
            'semester_credits': {
                'name': 'Semester term and credit hours',
                'keywords': [r'fall|spring|summer', r'credit\s*hours?', r'\d+\s*credits?'],
                'patterns': [r'(fall|spring|summer)\s*\d{4}', r'\d+\s*credit\s*hours?']
            },
            'meeting_info': {
                'name': 'Class meeting days/times/location',
                'keywords': [r'monday|tuesday|wednesday|thursday|friday|saturday|sunday', 
                           r'\d{1,2}:\d{2}', r'room|building|location'],
                'patterns': [r'(mon|tue|wed|thu|fri|sat|sun)', r'\d{1,2}:\d{2}\s*(am|pm)?']
            },
            'instructor_info': {
                'name': 'Instructor name, contact information, and office hours',
                'keywords': [r'instructor|professor|dr\.', r'email|phone', r'office\s*hours?'],
                'patterns': [r'\b[A-Z][a-z]+\s+[A-Z][a-z]+', r'[\w\.-]+@[\w\.-]+\.\w+', 
                           r'office\s*hours?']
            },
            'course_description': {
                'name': 'University course description',
                'keywords': [r'course\s*description', r'description'],
                'patterns': [r'course\s*description\s*:']
            },
            'prerequisites': {
                'name': 'Course prerequisites',
                'keywords': [r'prerequisite', r'prereq', r'required\s*courses?'],
                'patterns': [r'prerequisite\s*:?', r'prereq\s*:?']
            },
            'learning_outcomes': {
                'name': 'Student learning outcomes',
                'keywords': [r'learning\s*outcomes?', r'objectives?', r'students?\s*will'],
                'patterns': [r'learning\s*outcomes?\s*:?', r'course\s*objectives?\s*:?']
            },
            'required_materials': {
                'name': 'Required texts and/or course materials',
                'keywords': [r'textbook', r'required\s*text', r'materials?', r'isbn'],
                'patterns': [r'required\s*(text|materials?)\s*:?', r'textbook\s*:?']
            },
            'course_schedule': {
                'name': 'Course schedule',
                'keywords': [r'schedule', r'calendar', r'week\s*\d+', r'topics?'],
                'patterns': [r'course\s*schedule\s*:?', r'weekly\s*schedule']
            },
            'final_exam': {
                'name': 'Final exam date and time',
                'keywords': [r'final\s*exam', r'final\s*assessment'],
                'patterns': [r'final\s*exam\s*:?']
            },
            'grading_scale': {
                'name': 'Grading scale',
                'keywords': [r'grading\s*scale', r'grade\s*scale', r'a\s*=\s*\d+', r'\d+\s*-\s*\d+\s*=\s*[a-f]'],
                'patterns': [r'grading\s*scale\s*:?', r'[a-f]\s*[:=]\s*\d+']
            },
            'grade_weights': {
                'name': 'Grade categories and weights',
                'keywords': [r'weights?', r'percentage', r'\d+%', r'assignments?.*\d+%'],
                'patterns': [r'\d+\s*%', r'weights?\s*:?']
            },
            'syllabus_policy_link': {
                'name': 'Link to VCU Syllabus Policy Statements',
                'keywords': [r'syllabus\s*policy', r'provost', r'vcu.*policy'],
                'patterns': [r'provost.*website', r'https?://[^\s]*provost[^\s]*']
            },
            'library_statement': {
                'name': 'VCU Libraries statement and link',
                'keywords': [r'vcu\s*libraries?', r'library\.vcu\.edu'],
                'patterns': [r'https?://.*library\.vcu\.edu']
            }
        }
        
        self.recommended = {
            'attendance_policy': {
                'name': 'Attendance and punctuality policies',
                'keywords': [r'attendance', r'punctuality', r'absent'],
                'patterns': [r'attendance\s*policy']
            },
            'technology_policy': {
                'name': 'Technology and media policies',
                'keywords': [r'recording', r'email\s*response', r'technology', r'laptop', r'phone'],
                'patterns': [r'technology\s*policy', r'recording\s*policy']
            }
        }
    
    def extract_text_from_pdf(self, filepath):
        """Extract text from PDF file"""
        text = ""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text
    
    def extract_text_from_docx(self, filepath):
        """Extract text from DOCX file"""
        text = ""
        try:
            doc = Document(filepath)
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        return text
    
    def extract_text_from_txt(self, filepath):
        """Extract text from TXT file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
        except Exception as e:
            raise Exception(f"Error reading TXT: {str(e)}")
        return text
    
    def extract_text(self, filepath):
        """Extract text from various file formats"""
        _, ext = os.path.splitext(filepath.lower())
        
        if ext == '.pdf':
            return self.extract_text_from_pdf(filepath)
        elif ext == '.docx':
            return self.extract_text_from_docx(filepath)
        elif ext == '.txt':
            return self.extract_text_from_txt(filepath)
        else:
            raise Exception(f"Unsupported file format: {ext}")
    
    def check_requirement(self, text, requirement_data):
        """Check if a requirement is met in the text"""
        text_lower = text.lower()
        
        # Count matches
        matches = 0
        total_checks = len(requirement_data['keywords']) + len(requirement_data['patterns'])
        
        # Check keywords
        for keyword in requirement_data['keywords']:
            if re.search(keyword, text_lower, re.IGNORECASE):
                matches += 1
        
        # Check patterns
        for pattern in requirement_data['patterns']:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
        
        # Consider it found if at least 30% of checks match
        confidence = (matches / total_checks) * 100 if total_checks > 0 else 0
        found = confidence >= 30
        
        return {
            'found': found,
            'confidence': round(confidence, 1)
        }
    
    def check_syllabus(self, filepath):
        """Check syllabus against all requirements"""
        try:
            # Extract text from file
            text = self.extract_text(filepath)
            
            if not text or len(text.strip()) < 100:
                return {
                    'error': 'Unable to extract sufficient text from the file. Please ensure the file is not empty or corrupted.'
                }
            
            # Check required items
            required_results = []
            required_found = 0
            
            for key, req_data in self.requirements.items():
                result = self.check_requirement(text, req_data)
                required_results.append({
                    'name': req_data['name'],
                    'found': result['found'],
                    'confidence': result['confidence']
                })
                if result['found']:
                    required_found += 1
            
            # Check recommended items
            recommended_results = []
            recommended_found = 0
            
            for key, rec_data in self.recommended.items():
                result = self.check_requirement(text, rec_data)
                recommended_results.append({
                    'name': rec_data['name'],
                    'found': result['found'],
                    'confidence': result['confidence']
                })
                if result['found']:
                    recommended_found += 1
            
            # Calculate overall score
            total_required = len(self.requirements)
            required_percentage = (required_found / total_required) * 100
            
            return {
                'success': True,
                'required': {
                    'total': total_required,
                    'found': required_found,
                    'percentage': round(required_percentage, 1),
                    'items': required_results
                },
                'recommended': {
                    'total': len(self.recommended),
                    'found': recommended_found,
                    'items': recommended_results
                },
                'text_length': len(text)
            }
        
        except Exception as e:
            return {
                'error': str(e)
            }
