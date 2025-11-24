import re
import PyPDF2
from docx import Document
import os
from urllib.parse import urlparse

class SyllabusChecker:
    def __init__(self):
        # Enhanced requirement definitions with multiple detection strategies
        self.requirements = {
            'course_info': {
                'name': 'Course prefix and number, section number, and title',
                'primary_patterns': [
                    r'\b[A-Z]{2,4}\s*-?\s*\d{3,4}',  # BIOL 3001, CHEM-2001
                    r'(?i)section\s*:?\s*#?\s*\d+',  # Section: 001, Section #1
                ],
                'context_keywords': ['course', 'class', 'section', 'prefix', 'number'],
                'min_matches': 1
            },
            'semester_credits': {
                'name': 'Semester term and credit hours',
                'primary_patterns': [
                    r'(?i)(fall|spring|summer|winter)\s+\d{4}',  # Fall 2024
                    r'\d+\s*credit\s*hours?',  # 3 credit hours
                    r'\d+\s*credits?(?!\s*towards)',  # 3 credits
                    r'(?i)semester:\s*(fall|spring|summer)',
                ],
                'context_keywords': ['semester', 'term', 'credit', 'hours'],
                'min_matches': 1
            },
            'meeting_info': {
                'name': 'Class meeting days/times/location',
                'primary_patterns': [
                    r'\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?',  # 2:00 PM
                    r'(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
                    r'(?i)(mon|tue|wed|thu|fri|sat|sun)[\s,]',
                    r'(?i)room\s*:?\s*\w+\d+',  # Room: 101, Room B201
                    r'(?i)building\s*:?\s*\w+',
                    r'(?i)(harris|cabell|snead|rhoads|shafer|temple)\s+(hall|building)',  # VCU buildings
                ],
                'context_keywords': ['class', 'meeting', 'time', 'location', 'room', 'building'],
                'min_matches': 2
            },
            'instructor_info': {
                'name': 'Instructor name, contact information, and office hours',
                'primary_patterns': [
                    r'(?i)(instructor|professor|dr\.?|teacher)\s*:?\s*[A-Z][a-z]+\s+[A-Z][a-z]+',
                    r'[\w\.-]+@[\w\.-]+\.edu',  # Email
                    r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # Phone
                    r'(?i)office\s*hours?\s*:?',
                    r'(?i)email\s*:?\s*[\w\.-]+@',
                ],
                'context_keywords': ['instructor', 'professor', 'contact', 'email', 'phone', 'office'],
                'min_matches': 2
            },
            'course_description': {
                'name': 'University course description',
                'primary_patterns': [
                    r'(?i)course\s*description\s*:?',
                    r'(?i)description\s*:?\s*(?:this\s+course|students\s+will)',
                    r'(?i)(?:this\s+course|the\s+course)\s+(?:provides|introduces|explores|examines|covers)',
                ],
                'context_keywords': ['description', 'course', 'covers', 'introduces', 'explores'],
                'min_matches': 1,
                'min_text_length': 50  # Description should be substantial
            },
            'prerequisites': {
                'name': 'Course prerequisites',
                'primary_patterns': [
                    r'(?i)prerequisite\s*:?',
                    r'(?i)prereq\s*:?',
                    r'(?i)required\s+courses?\s*:?',
                    r'(?i)(?:none|no\s+prerequisites)',  # Also detect when there are none
                    r'(?i)students?\s+must\s+have\s+(?:completed|taken)',
                ],
                'context_keywords': ['prerequisite', 'prereq', 'required', 'prior', 'before'],
                'min_matches': 1
            },
            'learning_outcomes': {
                'name': 'Student learning outcomes',
                'primary_patterns': [
                    r'(?i)learning\s*outcomes?\s*:?',
                    r'(?i)course\s*objectives?\s*:?',
                    r'(?i)(?:upon\s+completion|by\s+the\s+end).*students?\s+(?:will|should)',
                    r'(?i)students?\s+will\s+be\s+able\s+to',
                    r'(?i)learning\s+goals?\s*:?',
                ],
                'context_keywords': ['learning', 'outcome', 'objective', 'goal', 'students will'],
                'min_matches': 1
            },
            'required_materials': {
                'name': 'Required texts and/or course materials',
                'primary_patterns': [
                    r'(?i)required\s+(?:text|book|material|reading)s?\s*:?',
                    r'(?i)textbooks?\s*:?',
                    r'(?i)course\s+materials?\s*:?',
                    r'ISBN[:\s-]*\d',
                    r'(?i)(?:required|recommended)\s+readings?\s*:?',
                ],
                'context_keywords': ['textbook', 'required', 'material', 'isbn', 'reading'],
                'min_matches': 1
            },
            'course_schedule': {
                'name': 'Course schedule',
                'primary_patterns': [
                    r'(?i)(?:course|class|weekly|tentative)\s*schedule\s*:?',
                    r'(?i)week\s+\d+\s*:?',
                    r'(?i)(?:calendar|timeline)\s*:?',
                    r'(?i)(?:week|session|class)\s+\d+.*(?:topic|chapter)',
                    r'(?i)(?:date|dates?)\s+(?:topic|chapter|reading)',
                    r'(?i)module\s+\d+\s*:?',  # "Module 1: Introduction"
                    r'(?i)(?:lesson|unit)\s+\d+',  # "Lesson 1", "Unit 1"
                    r'(?i)(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d+.*(?:topic|chapter|reading)',  # Date-based
                    r'(?i)\d{1,2}/\d{1,2}.*(?:topic|chapter|assignment)',  # "9/1 - Topic: Intro"
                    r'(?i)(?:see|refer to|attached)\s+(?:schedule|calendar)',  # References to external schedule
                ],
                'context_keywords': ['schedule', 'week', 'calendar', 'topic', 'date', 'module', 'lesson', 'unit'],
                'min_matches': 1  # Reduced from 2 - any clear schedule indicator
            },
            'final_exam': {
                'name': 'Final exam date and time',
                'primary_patterns': [
                    r'(?i)final\s+exam\s*:?',
                    r'(?i)final\s+assessment\s*:?',
                    r'(?i)final\s+examination\s*:?',
                    r'(?i)(?:final|exam)\s+(?:date|time|schedule)',
                    r'(?i)(?:no\s+final\s+exam|final\s+project\s+instead)',  # Also detect alternatives
                ],
                'context_keywords': ['final', 'exam', 'examination', 'assessment'],
                'min_matches': 1
            },
            'grading_scale': {
                'name': 'Grading scale',
                'primary_patterns': [
                    r'(?i)grading\s*scale\s*:?',
                    r'(?i)grade\s*scale\s*:?',
                    r'(?i)letter\s*grades?\s*:?',
                    r'[A-F]\s*[=:≥≤><]\s*\d+\.?\d*',  # A = 90, A ≥ 89.01, A > 90
                    r'\d+\.?\d*\s*[-–]\s*\d+\.?\d*\s*[=:]\s*[A-F]',  # 90-100 = A, 89.01-100 = A
                    r'(?i)(?:94|90).*?[=:≥>]\s*a',  # Common A cutoffs with various operators
                    # Synonyms for "scale"
                    r'(?i)grading\s*(?:rubric|criteria|standards?)\s*:?',  # "Grading rubric"
                    r'(?i)grade\s*(?:rubric|criteria|standards?)\s*:?',  # "Grade criteria"
                    r'(?i)grading\s*(?:system|scheme|structure)\s*:?',  # "Grading system"
                    r'(?i)grade\s*(?:system|scheme|structure)\s*:?',  # "Grade scheme"
                    r'(?i)letter\s*grade\s*(?:distribution|assignment)\s*:?',  # "Letter grade distribution"
                    r'(?i)(?:final|course)\s*grade\s*(?:determination|calculation)\s*:?',  # "Final grade determination"
                    r'(?i)grading\s*(?:policy|guidelines?)\s*:?',  # "Grading policy"
                    r'(?i)(?:how|basis\s+for)\s+(?:final\s+)?grades?\s+(?:are\s+)?(?:determined|assigned|calculated)',  # "How grades are determined"
                    r'(?i)grade\s+ranges?\s*:?',  # "Grade ranges"
                    r'(?i)percentage\s+(?:scale|breakdown|ranges?)\s*:?',  # "Percentage scale"
                    r'(?i)numeric\s+(?:grade|grading)\s*:?',  # "Numeric grading"
                    # Percentage-based scales
                    r'[A-F]\s*[=:≥≤><]\s*\d+\.?\d*\s*%',  # A = 90%, A > 89.999%
                    r'\d+\.?\d*\s*%\s*[-–]\s*\d+\.?\d*\s*%\s*[=:]\s*[A-F]',  # 90%-100% = A
                    r'[A-F]\s*[=:≥≤><]\s*\d+\.?\d*\s*[-–]\s*\d+\.?\d*\s*%',  # A = 90-100%, A ≥ 90%
                    # Decimal-based scales (GPA style)
                    r'[A-F][+-]?\s*[=:]\s*[0-4]\.\d+',  # A = 4.0, B+ = 3.3
                    r'[0-4]\.\d+\s*[=:]\s*[A-F]',  # 4.0 = A
                    r'(?i)(?:gpa|grade\s+point)\s*(?:scale|equivalent)',  # GPA scale
                    # Points-based scales
                    r'[A-F]\s*[=:≥≤><]\s*\d+\.?\d*\s*(?:[-–]\s*\d+\.?\d*\s*)?(?:total\s+)?(?:points?|pts)\.?',  # A ≥ 89.01 total pts.
                    r'\d+\.?\d*\s*[-–]\s*\d+\.?\d*\s*(?:points?|pts)\s*[=:]\s*[A-F]',  # 90-100 points = A
                    r'(?i)(?:points?|pts)\s*(?:scale|system|based)',  # Points scale
                    r'(?i)out\s+of\s+\d+\.?\d*\s*(?:total\s+)?(?:points?|pts)',  # out of 1000 points, out of 100.5 total pts
                ],
                'context_keywords': ['grading', 'grade', 'scale', 'letter', 'percentage', 'rubric', 'criteria', 'system', 'scheme', 'ranges', 'points', 'gpa', 'decimal', 'total', 'distribution'],
                'min_matches': 2  # Need actual scale, not just mention
            },
            'grade_weights': {
                'name': 'Grade categories and weights',
                'primary_patterns': [
                    r'\d+\s*%',  # Percentage
                    r'(?i)(?:weight|weigh)s?\s*:?',
                    r'(?i)(?:exam|quiz|homework|assignment|project|participation)s?\s*[:=]\s*\d+\s*%',
                    r'(?i)grade\s+(?:breakdown|composition|distribution)\s*:?',
                    r'(?i)(?:worth|counts?\s+(?:for|as))\s+\d+\s*%',
                    r'(?i)(?:exam|quiz|test)s?\s+\d+%',  # "Exams 40%"
                    r'(?i)(?:total|sum)\s+(?:points|pts)',  # Point-based systems
                    r'\d+\s*(?:points|pts)\s*(?:each|total)',  # "100 points each"
                    r'(?i)(?:grading|grade)\s+(?:policy|breakdown|criteria)',  # Alternative headers
                ],
                'context_keywords': ['weight', 'percent', 'breakdown', 'distribution', 'points', 'grade', 'evaluation'],
                'min_matches': 2  # Reduced from 3 to catch more edge cases
            },
            'syllabus_policy_link': {
                'name': 'Link to VCU Syllabus Policy Statements',
                'url_patterns': [
                    r'https?://[^\s]*provost[^\s]*',
                    r'https?://provost\.vcu\.edu',
                    r'https?://[^\s]*vcu\.edu[^\s]*(?:provost|syllabus|policy)',
                ],
                'text_patterns': [
                    r'(?i)vcu\s+syllabus\s+polic(?:y|ies)',
                    r'(?i)provost.*?(?:website|web\s+site|policies)',
                    r'(?i)syllabus\s+polic(?:y|ies).*?statements?',
                    r'(?i)university\s+syllabus\s+(?:requirements|policies)',
                ],
                'context_keywords': ['provost', 'syllabus', 'policy', 'vcu', 'university'],
                'min_matches': 1,
                'check_urls': True
            },
            'library_statement': {
                'name': 'VCU Libraries statement and link',
                'url_patterns': [
                    r'https?://(?:www\.)?library\.vcu\.edu',
                    r'https?://[^\s]*vcu\.edu[^\s]*library',
                ],
                'text_patterns': [
                    r'(?i)vcu\s+libraries?',
                    r'(?i)use\s+vcu\s+libraries?',
                    r'(?i)library\s+resources',
                    r'(?i)libraries?\s+(?:to\s+)?find\s+and\s+access',
                    r'(?i)library.*?(?:resources|services|support)',
                ],
                'required_phrases': [
                    r'(?i)vcu\s+libraries',
                    r'(?i)library\.vcu\.edu'
                ],
                'context_keywords': ['library', 'libraries', 'vcu', 'resources', 'access'],
                'min_matches': 2,
                'check_urls': True
            }
        }
        
        self.recommended = {
            'attendance_policy': {
                'name': 'Attendance and punctuality policies',
                'primary_patterns': [
                    r'(?i)attendance\s+polic(?:y|ies)\s*:?',
                    r'(?i)(?:absence|absent)s?\s*:?',
                    r'(?i)punctuality',
                    r'(?i)late\s+(?:arrival|attendance)',
                    r'(?i)(?:missing|miss)\s+(?:class|classes)',
                ],
                'context_keywords': ['attendance', 'absence', 'punctuality', 'late', 'present'],
                'min_matches': 1
            },
            'technology_policy': {
                'name': 'Technology and media policies',
                'primary_patterns': [
                    r'(?i)technology\s+polic(?:y|ies)\s*:?',
                    r'(?i)(?:recording|recordings?)\s+(?:of\s+)?(?:class|lecture)s?',
                    r'(?i)email\s+(?:response|policy)',
                    r'(?i)(?:laptop|phone|device)s?\s+(?:policy|use)',
                    r'(?i)(?:cell|mobile)\s+phones?',
                ],
                'context_keywords': ['technology', 'recording', 'email', 'laptop', 'phone', 'device'],
                'min_matches': 1
            }
        }

    def extract_urls(self, text):
        """Extract all URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text, re.IGNORECASE)
        # Clean up URLs (remove trailing punctuation)
        cleaned_urls = []
        for url in urls:
            url = re.sub(r'[.,;:!?)]+$', '', url)
            cleaned_urls.append(url)
        return cleaned_urls
    
    def extract_text_from_pdf(self, filepath):
        """Extract text from PDF file with better handling"""
        text = ""
        try:
            with open(filepath, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            raise Exception(f"Error reading PDF: {str(e)}")
        return text
    
    def extract_text_from_docx(self, filepath):
        """Extract text from DOCX file including hyperlinks"""
        text = ""
        try:
            doc = Document(filepath)
            # Extract paragraph text
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            # Also try to extract hyperlinks
            for rel in doc.part.rels.values():
                if "hyperlink" in rel.reltype:
                    if hasattr(rel, '_target'):
                        text += f" {rel._target} "
        except Exception as e:
            raise Exception(f"Error reading DOCX: {str(e)}")
        return text
    
    def extract_text_from_txt(self, filepath):
        """Extract text from TXT file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                text = file.read()
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(filepath, 'r', encoding='latin-1') as file:
                    text = file.read()
            except Exception as e:
                raise Exception(f"Error reading TXT: {str(e)}")
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
    
    def find_context_around_keyword(self, text, keyword_pattern, context_chars=200):
        """Find text context around a keyword match"""
        matches = re.finditer(keyword_pattern, text, re.IGNORECASE)
        contexts = []
        for match in matches:
            start = max(0, match.start() - context_chars)
            end = min(len(text), match.end() + context_chars)
            context = text[start:end]
            contexts.append(context)
        return contexts
    
    def check_requirement_enhanced(self, text, requirement_data, extracted_urls=None):
        """Enhanced requirement checking with multiple strategies"""
        text_lower = text.lower()
        matches = 0
        match_details = []
        
        # Strategy 1: Check for URLs if applicable
        if requirement_data.get('check_urls') and extracted_urls:
            url_patterns = requirement_data.get('url_patterns', [])
            for url in extracted_urls:
                for pattern in url_patterns:
                    if re.search(pattern, url, re.IGNORECASE):
                        matches += 2  # URLs are strong indicators
                        match_details.append(f"Found URL: {url[:50]}...")
                        break
        
        # Strategy 2: Check primary patterns
        primary_patterns = requirement_data.get('primary_patterns', [])
        for pattern in primary_patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            if found:
                matches += 1
                match_details.append(f"Pattern match: {pattern[:30]}...")
        
        # Strategy 3: Check text patterns (for link requirements)
        text_patterns = requirement_data.get('text_patterns', [])
        for pattern in text_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                matches += 1
                match_details.append(f"Text pattern: {pattern[:30]}...")
        
        # Strategy 4: Check required phrases (must have these)
        required_phrases = requirement_data.get('required_phrases', [])
        required_found = 0
        for phrase in required_phrases:
            if re.search(phrase, text, re.IGNORECASE):
                required_found += 1
        
        # Strategy 5: Context-aware checking
        context_keywords = requirement_data.get('context_keywords', [])
        context_matches = 0
        for keyword in context_keywords:
            if re.search(r'\b' + keyword + r'\b', text_lower):
                context_matches += 1
        
        # Strategy 6: Check minimum text length for descriptions
        min_text_length = requirement_data.get('min_text_length', 0)
        has_sufficient_text = True
        if min_text_length > 0:
            # Find sections that might be the description
            primary_patterns = requirement_data.get('primary_patterns', [])
            for pattern in primary_patterns:
                contexts = self.find_context_around_keyword(text, pattern, 300)
                if contexts and len(contexts[0]) >= min_text_length:
                    has_sufficient_text = True
                    break
        
        # Calculate confidence score
        min_matches = requirement_data.get('min_matches', 1)
        
        # For requirements with required phrases, they must be present
        if required_phrases and required_found < len(required_phrases):
            # If required phrases are missing, confidence is low
            confidence = (matches / (len(primary_patterns) + len(text_patterns) + 2)) * 100
            confidence = min(confidence, 40)  # Cap at 40% if required phrases missing
        else:
            # Normal confidence calculation
            total_possible = len(primary_patterns) + len(text_patterns) + len(context_keywords)
            if requirement_data.get('check_urls'):
                total_possible += 2  # URLs count more
            
            if total_possible > 0:
                # Weighted scoring
                pattern_score = matches * 30
                context_score = (context_matches / len(context_keywords) * 20) if context_keywords else 0
                url_bonus = 20 if (extracted_urls and any(re.search(p, ' '.join(extracted_urls), re.IGNORECASE) for p in requirement_data.get('url_patterns', []))) else 0
                
                confidence = min(100, pattern_score + context_score + url_bonus)
            else:
                confidence = 0
        
        # Apply minimum matches requirement
        found = matches >= min_matches and has_sufficient_text
        
        # If confidence is very low, mark as not found
        if confidence < 25:
            found = False
        
        return {
            'found': found,
            'confidence': round(confidence, 1),
            'matches': matches,
            'details': match_details[:3]  # Keep top 3 details
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
            
            # Extract all URLs first
            extracted_urls = self.extract_urls(text)
            
            # Check required items
            required_results = []
            required_found = 0
            
            for key, req_data in self.requirements.items():
                result = self.check_requirement_enhanced(text, req_data, extracted_urls)
                required_results.append({
                    'name': req_data['name'],
                    'found': result['found'],
                    'confidence': result['confidence'],
                    'details': result.get('details', [])
                })
                if result['found']:
                    required_found += 1
            
            # Check recommended items
            recommended_results = []
            recommended_found = 0
            
            for key, rec_data in self.recommended.items():
                result = self.check_requirement_enhanced(text, rec_data, extracted_urls)
                recommended_results.append({
                    'name': rec_data['name'],
                    'found': result['found'],
                    'confidence': result['confidence'],
                    'details': result.get('details', [])
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
                'text_length': len(text),
                'urls_found': len(extracted_urls),
                'sample_urls': extracted_urls[:5]  # Include sample URLs for debugging
            }
        
        except Exception as e:
            return {
                'error': str(e)
            }
