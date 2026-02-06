import re
import PyPDF2
from docx import Document
import os
from urllib.parse import urlparse

# Import VCU Bulletin scraper
try:
    from vcu_bulletin_scraper import scrape_course_data
    BULLETIN_SCRAPER_AVAILABLE = True
except ImportError:
    BULLETIN_SCRAPER_AVAILABLE = False
    print("Warning: VCU Bulletin scraper not available. Install required packages: beautifulsoup4, requests, lxml")

class SyllabusChecker:
    def __init__(self):
        # Enhanced requirement definitions with multiple detection strategies
        # Requirements with sub-items have 'sub_items' field for granular checking
        self.requirements = {
            'course_info': {
                'name': 'Course information',
                'has_sub_items': True,
                'sub_items': {
                    'course_code': {
                        'name': 'Course prefix and number',
                        'weight': 0.34,  # ~1/3 of requirement
                        'primary_patterns': [
                            r'\b[A-Z]{2,4}\s*-?\s*\d{3,4}(?!-\d)',  # INFO 370, CHEM-2001 (but not INFO370-003)
                        ],
                        'context_keywords': ['course', 'class'],
                        'min_matches': 1
                    },
                    'section_number': {
                        'name': 'Section number',
                        'weight': 0.33,  # ~1/3 of requirement
                        'primary_patterns': [
                            r'(?i)section\s*:?\s*#?\s*\d+',  # Section: 001, Section #1
                            r'(?i)section\s*:?\s*#?\s*[0-9]{3}',  # Section 001
                            r'\b[A-Z]{2,4}\s*\d{3,4}-\d{3}',  # INFO370-003
                        ],
                        'context_keywords': ['section'],
                        'min_matches': 1
                    },
                    'course_title': {
                        'name': 'Course title',
                        'weight': 0.33,  # ~1/3 of requirement
                        'primary_patterns': [
                            r'(?i)(?:course\s+)?title\s*:?\s*.{10,}',  # Course Title: ...
                            r'(?i)course\s+name\s*:?\s*.{10,}',  # Course Name: ...
                        ],
                        'context_keywords': ['title', 'name'],
                        'min_matches': 1,
                        'use_bulletin_validation': True  # Will validate against official title
                    }
                }
            },
            'semester_credits': {
                'name': 'Semester and credit information',
                'has_sub_items': True,
                'sub_items': {
                    'semester_term': {
                        'name': 'Semester term',
                        'weight': 0.5,  # 1/2 of requirement
                        'primary_patterns': [
                            r'(?i)(fall|spring|summer|winter)\s+\d{4}',  # Fall 2024
                            r'(?i)semester:\s*(fall|spring|summer|winter)',
                            r'(?i)(fall|spring|summer|winter)\s+(semester|term)',
                        ],
                        'context_keywords': ['semester', 'term', 'fall', 'spring', 'summer', 'winter'],
                        'min_matches': 1
                    },
                    'credit_hours': {
                        'name': 'Credit hours',
                        'weight': 0.5,  # 1/2 of requirement
                        'primary_patterns': [
                            r'\d+\s*credit\s*hours?',  # 3 credit hours
                            r'\d+\s*credits?(?!\s*towards)',  # 3 credits
                            r'(?i)\d+\s*(?:semester\s+)?(?:hour|hr)s?',  # 3 semester hours
                        ],
                        'context_keywords': ['credit', 'hours', 'credits'],
                        'min_matches': 1
                    }
                }
            },
            'meeting_info': {
                'name': 'Class meeting information',
                'has_sub_items': True,
                'sub_items': {
                    'meeting_days': {
                        'name': 'Meeting days',
                        'weight': 0.33,  # ~1/3 of requirement
                        'primary_patterns': [
                            r'(?i)(monday|tuesday|wednesday|thursday|friday|saturday|sunday)',
                            r'(?i)(mon|tue|wed|thu|fri|sat|sun)[\s,]',
                            r'(?i)(?:m|t|w|th|f)\s*(?:&|and)\s*(?:m|t|w|th|f)',  # MW, TR
                        ],
                        'context_keywords': ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'days'],
                        'min_matches': 1
                    },
                    'meeting_time': {
                        'name': 'Meeting time',
                        'weight': 0.33,  # ~1/3 of requirement
                        'primary_patterns': [
                            r'\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?',  # 2:00 PM
                            r'(?i)\d{1,2}:\d{2}\s*(?:a\.?m\.?|p\.?m\.?)',
                            r'(?i)time\s*:?\s*\d{1,2}:\d{2}',
                        ],
                        'context_keywords': ['time', 'meets'],
                        'min_matches': 1
                    },
                    'meeting_location': {
                        'name': 'Meeting location',
                        'weight': 0.34,  # ~1/3 of requirement
                        'primary_patterns': [
                            # Physical locations
                            r'(?i)room\s*:?\s*\w+\d+',  # Room: 101, Room B201
                            r'(?i)building\s*:?\s*\w+',
                            r'(?i)(harris|cabell|snead|rhoads|shafer|temple)\s+(hall|building)',  # VCU buildings
                            r'(?i)location\s*:?\s*\w+',

                            # Online/Virtual locations
                            r'(?i)\bonline\b',  # online
                            r'(?i)\bvirtual(?:ly)?\b',  # virtual, virtually
                            r'(?i)\bremote(?:ly)?\b',  # remote, remotely
                            r'(?i)\bzoom\b',  # Zoom
                            r'(?i)\b(?:a?sync(?:hronous)?)\s+online\b',  # synchronous online, asynchronous online, async online
                            r'(?i)\b(?:fully\s+)?online\s+(?:course|class)\b',  # fully online course
                            r'(?i)(?:via|through|using)\s+(?:zoom|teams|canvas|blackboard|webex|google\s+meet)',  # via Zoom, through Teams
                            r'(?i)microsoft\s+teams',  # Microsoft Teams
                            r'(?i)google\s+meet',  # Google Meet
                            r'(?i)distance\s+learning',  # distance learning
                        ],
                        'context_keywords': ['room', 'building', 'location', 'hall', 'online', 'zoom', 'virtual', 'remote', 'asynchronous', 'synchronous'],
                        'min_matches': 1
                    }
                }
            },
            'instructor_info': {
                'name': 'Instructor information',
                'has_sub_items': True,
                'sub_items': {
                    'instructor_name': {
                        'name': 'Instructor name',
                        'weight': 0.33,  # ~1/3 of requirement
                        'primary_patterns': [
                            r'(?i)(instructor|professor|dr\.?|teacher)\s*:?\s*[A-Z][a-z]+\s+[A-Z][a-z]+',
                            r'(?i)taught\s+by\s*:?\s*[A-Z][a-z]+',
                        ],
                        'context_keywords': ['instructor', 'professor', 'teacher', 'dr', 'taught'],
                        'min_matches': 1
                    },
                    'contact_info': {
                        'name': 'Contact information',
                        'weight': 0.33,  # ~1/3 of requirement
                        'primary_patterns': [
                            r'[\w\.-]+@[\w\.-]+\.edu',  # Email
                            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # Phone
                            r'(?i)email\s*:?\s*[\w\.-]+@',
                            r'(?i)phone\s*:?\s*\(?\d{3}\)?',
                        ],
                        'context_keywords': ['email', 'phone', 'contact'],
                        'min_matches': 1
                    },
                    'office_hours': {
                        'name': 'Office hours',
                        'weight': 0.34,  # ~1/3 of requirement
                        'primary_patterns': [
                            r'(?i)office\s*hours?\s*:?',
                            r'(?i)office\s*:?\s*(?:mon|tue|wed|thu|fri)',
                            r'(?i)available\s*:?\s*(?:mon|tue|wed|thu|fri)',
                        ],
                        'context_keywords': ['office', 'hours', 'available', 'appointment'],
                        'min_matches': 1
                    }
                }
            },
            'course_description': {
                'name': 'University course description',
                'primary_patterns': [
                    r'(?i)course\s*description\s*:?',
                    r'(?i)description\s*:?\s*(?:this\s+course|students\s+will)',
                    r'(?i)(?:this\s+course|the\s+course)\s+(?:provides|introduces|explores|examines|covers)',
                    r'(?i)course\s*overview',  # "Course Overview"
                    r'(?i)catalog\s*description',  # "Catalog Description"
                    r'(?i)(?:from|per)\s+(?:the\s+)?(?:vcu\s+)?bulletin',  # "From VCU Bulletin"
                ],
                'context_keywords': ['description', 'course', 'covers', 'introduces', 'explores', 'overview', 'bulletin'],
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
                    r'(?i)students?\s+must\s+have\s+(?:completed|taken|passed)',
                ],
                'context_keywords': ['prerequisite', 'prereq', 'required', 'prior', 'before'],
                'min_matches': 1
            },
            'learning_outcomes': {
                'name': 'Student learning outcomes',
                'primary_patterns': [
                    r'(?i)(learning|course)\s*(outcomes|objectives)?\s*:?',
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
                    r'(?i)(?:course|class)\s*(?:calendar|timeline)\s*:?',  # Made stricter to avoid "Academic Calendar"
                    r'(?i)(?:week|session|class)\s+\d+.*(?:topic|chapter)',
                    r'(?i)(?:day|dates?)\s+(?:topic|chapter|reading)',
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
                    r'(?i)(?:no\s+final\s+exam|final\s+project\s+instead)',  # Explicit alternatives
                    r'(?i)final\s+project\s*:?',  # Final project
                ],
                'context_keywords': ['final', 'exam', 'examination', 'assessment', 'project'],
                'min_matches': 1
            },
            'grading_scale': {
                'name': 'Grading scale',
                'primary_patterns': [
                    r'(?i)grading\s*scale\s*:?',
                    r'(?i)grade\s*scale\s*:?',
                    r'(?i)letter\s*grades?\s*:?',
                    r'[A-F]\s*(?:>=|<=|[=:≥≤><])\s*\d+\.?\d*',  # A = 90, A >= 90, A ≥ 89.01, A > 90
                    r'\d+\.?\d*\s*[-–]\s*\d+\.?\d*\s*[=:]\s*[A-F]',  # 90-100 = A, 89.01-100 = A
                    r'(?i)(?:94|90).*?(?:>=|[=:≥>])\s*a',  # Common A cutoffs with various operators
                    r'(?i)[A-F]\s+\d+\.?\d*\s+(?:and\s+)?(?:above|or\s+(?:higher|greater))',  # A 90 and above, B 80 or higher
                    r'(?i)[A-F]\s+\d+\.?\d*\s*%?\s*(?:and\s+)?(?:above|or\s+(?:higher|greater))',  # A 90% and above
                    r'(?i)[A-F]\s+\d+\.?\d*\s+(?:and\s+)?(?:below|or\s+(?:lower|less))',  # F 59 and below, F 60 or lower
                    r'(?i)[A-F]\s+\d+\.?\d*\s*%?\s*(?:and\s+)?(?:below|or\s+(?:lower|less))',  # F 59% and below
                    
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
                    r'[A-F]\s*(?:>=|<=|[=:≥≤><])\s*\d+\.?\d*\s*%',  # A = 90%, A >= 90%, A > 89.999%
                    r'\d+\.?\d*\s*%\s*[-–]\s*\d+\.?\d*\s*%\s*[=:]\s*[A-F]',  # 90%-100% = A
                    r'[A-F]\s*(?:>=|<=|[=:≥≤><])\s*\d+\.?\d*\s*[-–]\s*\d+\.?\d*\s*%',  # A = 90-100%, A >= 90%
                    
                    # Points-based scales
                    r'[A-F]\s*(?:>=|<=|[=:≥≤><])\s*\d+\.?\d*\s*(?:[-–]\s*\d+\.?\d*\s*)?(?:total\s+)?(?:points?|pts)\.?',  # A >= 89.01 total pts, A ≥ 89.01 total pts.
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
                    # AI Policy patterns - comprehensive coverage
                    r'(?i)(?:artificial\s+intelligence|AI)\s+polic(?:y|ies)',  # AI Policy
                    r'(?i)polic(?:y|ies)\s+(?:on|regarding|for)\s+(?:artificial\s+intelligence|AI)',  # Policy on AI
                    r'(?i)(?:generative\s+)?AI\s+(?:use|tools?|policy)',  # AI use/tools/policy
                    r'(?i)(?:use|usage)\s+of\s+(?:artificial\s+intelligence|AI)',  # Use of AI
                    r'(?i)(?:artificial\s+intelligence|AI)\s+(?:is\s+)?(?:allowed|permitted|prohibited|forbidden)',  # AI allowed/prohibited
                    r'(?i)(?:AI|artificial\s+intelligence).*?(?:policy|guideline|rule)',  # AI mentioned with policy terms
                ],
                'context_keywords': ['technology', 'recording', 'email', 'laptop', 'phone', 'device', 'ai', 'chatgpt', 'intelligence', 'artificial', 'llm', 'generative'],
                'min_matches': 2
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
            
            # Auto-detect course code and scrape bulletin data
            bulletin_data = None
            course_prefix, course_number = self.extract_course_code(text)
            
            if course_prefix and course_number and BULLETIN_SCRAPER_AVAILABLE:
                try:
                    bulletin_data = scrape_course_data(course_prefix, course_number)
                except Exception as e:
                    # If scraping fails, log but continue with pattern-only checking
                    print(f"Bulletin scraping failed for {course_prefix} {course_number}: {e}")
                    bulletin_data = None
            
            # Check required items
            required_results = []
            required_found = 0
            
            for key, req_data in self.requirements.items():
                # Check if this requirement has sub-items
                if req_data.get('has_sub_items'):
                    # Check each sub-item separately
                    sub_results = []
                    total_weight_found = 0.0
                    
                    for sub_key, sub_data in req_data['sub_items'].items():
                        # Special handling for course_title with bulletin validation
                        if sub_key == 'course_title' and sub_data.get('use_bulletin_validation') and bulletin_data and bulletin_data.get('found'):
                            official_title = bulletin_data.get('title')
                            if official_title and official_title.lower() in text.lower():
                                # Exact match found
                                sub_result = {
                                    'name': sub_data['name'],
                                    'found': True,
                                    'confidence': 100,
                                    'weight': sub_data['weight'],
                                    'bulletin_check': {
                                        'official_text': official_title,
                                        'exact_match': True,
                                        'validation_method': 'bulletin_exact_match'
                                    }
                                }
                                total_weight_found += sub_data['weight']
                            else:
                                # Check for close/partial match
                                similarity = self._calculate_title_similarity(official_title, text)
                                
                                if similarity >= 70:  # 70% similarity threshold
                                    # Close match found
                                    sub_result = {
                                        'name': sub_data['name'],
                                        'found': True,
                                        'confidence': int(similarity),
                                        'weight': sub_data['weight'],
                                        'bulletin_check': {
                                            'official_text': official_title,
                                            'exact_match': False,
                                            'validation_method': 'bulletin_partial_match',
                                            'similarity': similarity
                                        },
                                        'special_note': f"Note: Close match found ({int(similarity)}% similar). Official title: \"{official_title}\". Please verify this is correct."
                                    }
                                    total_weight_found += sub_data['weight']
                                else:
                                    # No match
                                    sub_result = {
                                        'name': sub_data['name'],
                                        'found': False,
                                        'confidence': 0,
                                        'weight': sub_data['weight'],
                                        'bulletin_check': {
                                            'official_text': official_title,
                                            'exact_match': False,
                                            'validation_method': 'bulletin_no_match'
                                        }
                                    }
                        else:
                            # Standard pattern checking for sub-item
                            sub_result_data = self.check_requirement_enhanced(text, sub_data, extracted_urls)
                            sub_result = {
                                'name': sub_data['name'],
                                'found': sub_result_data['found'],
                                'confidence': sub_result_data['confidence'],
                                'weight': sub_data['weight']
                            }
                            if sub_result_data['found']:
                                total_weight_found += sub_data['weight']
                        
                        sub_results.append(sub_result)
                    
                    # Calculate if the overall requirement is found (>= 0.5 means majority of components)
                    requirement_found = total_weight_found >= 0.5
                    
                    required_results.append({
                        'name': req_data['name'],
                        'found': requirement_found,
                        'confidence': int(total_weight_found * 100),  # Convert to percentage
                        'has_sub_items': True,
                        'sub_items': sub_results,
                        'partial_credit': total_weight_found  # Actual credit earned (0.0 to 1.0)
                    })
                    
                    # Add partial credit to required_found
                    required_found += total_weight_found
                    
                # Use bulletin validation for description and prerequisites if available
                elif key in ['course_description', 'prerequisites'] and bulletin_data and bulletin_data.get('found'):
                    # Get bulletin validation results
                    bulletin_validation = self.validate_description_and_prereqs_combined(text, bulletin_data)
                    
                    if key == 'course_description':
                        validation_result = bulletin_validation['description']
                    else:  # prerequisites
                        validation_result = bulletin_validation['prerequisites']
                    
                    # Create result with bulletin check information
                    required_results.append({
                        'name': req_data['name'],
                        'found': validation_result['found'],
                        'confidence': validation_result['confidence'],
                        'details': [f"Validation method: {validation_result['method']}"],
                        'bulletin_check': {
                            'official_text': validation_result['official_text'],
                            'exact_match': validation_result['found'] and validation_result['confidence'] == 100,
                            'validation_method': validation_result['method'],
                            'is_applicable': validation_result.get('is_applicable', True)
                        }
                    })
                    
                    if validation_result['found']:
                        required_found += 1
                else:
                    # Standard pattern-based checking
                    result = self.check_requirement_enhanced(text, req_data, extracted_urls)
                    
                    # Special handling for final_exam: check if final project was detected
                    special_note = None
                    if key == 'final_exam' and result['found']:
                        # Check if "final project" patterns matched
                        final_project_patterns = [
                            r'(?i)final\s+project\s*:?',
                            r'(?i)(?:no\s+final\s+exam|final\s+project\s+instead)'
                        ]
                        for pattern in final_project_patterns:
                            if re.search(pattern, text, re.IGNORECASE):
                                special_note = "Note: Final project detected instead of traditional final exam"
                                break
                    
                    details = result.get('details', [])
                    if special_note:
                        details.append(special_note)
                    
                    required_results.append({
                        'name': req_data['name'],
                        'found': result['found'],
                        'confidence': result['confidence'],
                        'details': details,
                        'special_note': special_note  # Add flag for frontend
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
                'sample_urls': extracted_urls[:5],  # Include sample URLs for debugging
                'bulletin_validation': {
                    'enabled': BULLETIN_SCRAPER_AVAILABLE,
                    'course_detected': f"{course_prefix} {course_number}" if course_prefix else None,
                    'bulletin_data_found': bulletin_data.get('found') if bulletin_data else False
                }
            }
        
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def extract_course_code(self, text):
        """
        Extract course prefix and number from syllabus text.
        
        Args:
            text: Full syllabus text
        
        Returns:
            tuple: (prefix, number) or (None, None) if not found
        """
        # Use the same pattern as in course_info requirement
        pattern = r'\b([A-Z]{2,4})\s*-?\s*(\d{3,4})\b'
        match = re.search(pattern, text)
        
        if match:
            return (match.group(1), match.group(2))
        
        return (None, None)
    
    def normalize_text(self, text):
        """
        Normalize text for comparison by:
        - Converting to lowercase
        - Collapsing multiple spaces/newlines to single space
        - Removing extra punctuation spaces
        
        Args:
            text: String to normalize
        
        Returns:
            str: Normalized text
        """
        if not text:
            return ""
        
        # Convert to lowercase
        normalized = text.lower()
        
        # Collapse multiple whitespace characters to single space
        normalized = re.sub(r'\s+', ' ', normalized)
        
        # Strip leading/trailing whitespace
        normalized = normalized.strip()
        
        return normalized
    
    def extract_prerequisite_courses(self, prereq_text):
        """
        Extract course codes from prerequisite text.
        
        Args:
            prereq_text: Text containing prerequisites (e.g., "MATH 211 and INFO 300")
        
        Returns:
            list: Course codes like ["MATH 211", "INFO 300"]
        """
        if not prereq_text:
            return []
        
        # Pattern matches course codes: MATH 211, INFO 300, CMSC 245, etc.
        pattern = r'\b([A-Z]{2,4})\s*-?\s*(\d{3,4})\b'
        matches = re.findall(pattern, prereq_text)
        
        # Combine prefix and number
        courses = [f"{prefix} {number}" for prefix, number in matches]
        
        return courses
    
    def validate_description_and_prereqs_combined(self, syllabus_text, bulletin_data):
        """
        Validate both description and prerequisites using combined-then-separate strategy.
        
        Strategy:
        1. First try: Search for complete bulletin paragraph (fast path)
           - If found → Both items validated, confidence 100%
        2. If not found: Check each separately (fallback)
           - Description: word-for-word match required
           - Prerequisites: flexible course code matching
        
        Args:
            syllabus_text: Full syllabus text
            bulletin_data: Data from VCU Bulletin with 'full_paragraph', 
                          'description', and 'prerequisites' fields
        
        Returns:
            dict: {
                'description': {
                    'found': True/False,
                    'confidence': 0-100,
                    'method': 'combined' | 'separate' | 'pattern_only',
                    'official_text': '...'
                },
                'prerequisites': {
                    'found': True/False,
                    'confidence': 0-100,
                    'method': 'combined' | 'separate' | 'pattern_only',
                    'official_text': '...'
                }
            }
        """
        result = {
            'description': {
                'found': False,
                'confidence': 0,
                'method': 'pattern_only',
                'official_text': None,
                'is_applicable': True
            },
            'prerequisites': {
                'found': False,
                'confidence': 0,
                'method': 'pattern_only',
                'official_text': None,
                'is_applicable': True
            }
        }
        
        # If bulletin data wasn't successfully retrieved, return pattern-only
        if not bulletin_data or not bulletin_data.get('found'):
            return result
        
        # Check if course has no prerequisites - mark as N/A if so
        prereq_text = bulletin_data.get('prerequisites')
        if not prereq_text or prereq_text == 'None' or re.search(r'^(none|no\s+prerequisites?)\.?$', str(prereq_text).strip(), re.IGNORECASE):
            result['prerequisites']['is_applicable'] = False
            result['prerequisites']['found'] = True  # Mark as found since N/A is satisfied
            result['prerequisites']['confidence'] = 100
            result['prerequisites']['method'] = 'not_applicable'
            result['prerequisites']['official_text'] = 'None'
            # Description still needs to be checked, so continue
        else:
            result['prerequisites']['is_applicable'] = True
        
        # Normalize texts for comparison
        syllabus_normalized = self.normalize_text(syllabus_text)
        
        # STEP 1: Try combined check (fast path)
        # Only do combined check if prerequisites are applicable
        if result['prerequisites']['is_applicable'] and bulletin_data.get('full_paragraph'):
            full_para_normalized = self.normalize_text(bulletin_data['full_paragraph'])
            
            if full_para_normalized in syllabus_normalized:
                # Found the complete paragraph - both validated!
                result['description']['found'] = True
                result['description']['confidence'] = 100
                result['description']['method'] = 'combined'
                result['description']['official_text'] = bulletin_data.get('description')
                
                result['prerequisites']['found'] = True
                result['prerequisites']['confidence'] = 100
                result['prerequisites']['method'] = 'combined'
                result['prerequisites']['official_text'] = bulletin_data.get('prerequisites', 'None')
                
                return result
        
        # STEP 2: Check separately (fallback)
        
        # Check description (word-for-word)
        if bulletin_data.get('description'):
            desc_normalized = self.normalize_text(bulletin_data['description'])
            result['description']['official_text'] = bulletin_data['description']
            
            if desc_normalized in syllabus_normalized:
                result['description']['found'] = True
                result['description']['confidence'] = 100
                result['description']['method'] = 'separate'
            else:
                # Check for close match (95%+ similarity)
                # Simple character-based similarity
                similarity = self._calculate_similarity(desc_normalized, syllabus_normalized)
                if similarity >= 95:
                    result['description']['found'] = True
                    result['description']['confidence'] = 85
                    result['description']['method'] = 'separate'
                else:
                    result['description']['found'] = False
                    result['description']['confidence'] = 0
                    result['description']['method'] = 'separate'
        
        # Check prerequisites (flexible course code matching)
        # Only check if prerequisites are applicable (not already marked as N/A)
        if result['prerequisites']['is_applicable'] and bulletin_data.get('prerequisites'):
            prereq_text = bulletin_data['prerequisites']
            result['prerequisites']['official_text'] = prereq_text
            
            # Extract prerequisite course codes
            required_courses = self.extract_prerequisite_courses(prereq_text)
            
            if required_courses:
                # Check if all required courses are mentioned in syllabus
                found_courses = []
                for course in required_courses:
                    if course in syllabus_text:
                        found_courses.append(course)
                
                if len(found_courses) == len(required_courses):
                    # All prerequisites found
                    result['prerequisites']['found'] = True
                    result['prerequisites']['confidence'] = 100
                    result['prerequisites']['method'] = 'separate'
                elif len(found_courses) > 0:
                    # Some prerequisites found
                    result['prerequisites']['found'] = False
                    result['prerequisites']['confidence'] = 50
                    result['prerequisites']['method'] = 'separate'
                else:
                    # No prerequisites found
                    result['prerequisites']['found'] = False
                    result['prerequisites']['confidence'] = 0
                    result['prerequisites']['method'] = 'separate'
        
        return result
    
    def _calculate_similarity(self, text1, text2): #what is this for?
        """
        Calculate simple similarity percentage between two texts.
        
        Args:
            text1: First text (typically shorter - description)
            text2: Second text (typically longer - full syllabus)
        
        Returns:
            float: Similarity percentage (0-100)
        """
        if not text1 or not text2:
            return 0.0
        
        # Check if text1 is substring of text2
        if text1 in text2:
            return 100.0
        
        # Simple character-based similarity
        # Count matching characters in order
        matches = 0
        text1_len = len(text1)
        
        for i, char in enumerate(text1):
            if i < len(text2) and text2[i] == char:
                matches += 1
        
        similarity = (matches / text1_len * 100) if text1_len > 0 else 0
        
        return similarity
    
    def _calculate_title_similarity(self, official_title, syllabus_text):
        """
        Calculate similarity between official course title and syllabus text.
        Uses word-based matching to handle reordered or slightly different titles.
        
        Args:
            official_title: Official course title from bulletin
            syllabus_text: Full syllabus text
        
        Returns:
            float: Similarity percentage (0-100)
        """
        if not official_title or not syllabus_text:
            return 0.0
        
        # Normalize texts
        official_lower = official_title.lower()
        syllabus_lower = syllabus_text.lower()
        
        # Check for exact match first
        if official_lower in syllabus_lower:
            return 100.0
        
        # Split title into significant words (ignore common words)
        stop_words = {'a', 'an', 'the', 'of', 'to', 'in', 'for', 'and', 'or', 'with'}
        title_words = [word.strip('.,;:!?') for word in official_lower.split() 
                      if word.strip('.,;:!?') not in stop_words and len(word.strip('.,;:!?')) > 2]
        
        if not title_words:
            return 0.0
        
        # Count how many significant title words appear in syllabus
        matched_words = sum(1 for word in title_words if word in syllabus_lower)
        
        # Calculate percentage
        word_match_percentage = (matched_words / len(title_words)) * 100
        
        # Also check for partial word matches (for abbreviations or variations)
        partial_matches = 0
        for word in title_words:
            if len(word) >= 4:  # Only for longer words
                # Check if first 4 characters match any word in syllabus
                word_start = word[:4]
                if word_start in syllabus_lower:
                    partial_matches += 0.5  # Half credit for partial match
        
        partial_match_percentage = (partial_matches / len(title_words)) * 100
        
        # Combine both scores (word matching weighted more heavily)
        final_similarity = (word_match_percentage * 0.8) + (partial_match_percentage * 0.2)
        
        return min(final_similarity, 100.0)  # Cap at 100%
