"""
VCU Bulletin Web Scraper
Scrapes course descriptions and prerequisites from bulletin.vcu.edu
"""

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time


# ============================================================================
# Caching Mechanism
# ============================================================================

class BulletinCache:
    """
    In-memory cache for VCU Bulletin data.
    
    NOTE: Cache is cleared when server restarts.
    TODO: Consider file-based or persistent cache based on 
          production deployment strategy.
    """
    
    def __init__(self, ttl_hours=1):
        self.cache = {}
        self.ttl_seconds = ttl_hours * 3600
    
    def get(self, course_key):
        """Get cached data if it exists and hasn't expired"""
        if course_key in self.cache:
            entry = self.cache[course_key]
            if datetime.now() < entry['expires_at']:
                return entry['data']
            else:
                # Expired, remove from cache
                del self.cache[course_key]
        return None
    
    def set(self, course_key, data):
        """Cache data with expiration timestamp"""
        self.cache[course_key] = {
            'data': data,
            'cached_at': datetime.now(),
            'expires_at': datetime.now() + timedelta(seconds=self.ttl_seconds)
        }
    
    def clear(self):
        """Clear all cache"""
        self.cache = {}


# Global cache instance
_bulletin_cache = BulletinCache(ttl_hours=1)


# ============================================================================
# Course Code Parsing
# ============================================================================

def parse_course_code(text):
    """
    Extract course prefix and number from text.
    
    Args:
        text: String containing course code (e.g., "INFO 370", "BIOL-3001")
    
    Returns:
        dict: {'prefix': 'INFO', 'number': '370', 'full_code': 'INFO 370'}
              or {'prefix': None, 'number': None, 'full_code': None} if not found
    """
    # Pattern matches: INFO 370, BIOL-3001, CMSC 245, etc.
    pattern = r'\b([A-Z]{2,4})\s*-?\s*(\d{3,4})\b'
    match = re.search(pattern, text)
    
    if match:
        prefix = match.group(1)
        number = match.group(2)
        return {
            'prefix': prefix,
            'number': number,
            'full_code': f"{prefix} {number}"
        }
    
    return {'prefix': None, 'number': None, 'full_code': None}


# ============================================================================
# URL Building
# ============================================================================

def build_bulletin_url(prefix):
    """
    Build URL for course prefix page on VCU Bulletin.
    
    Args:
        prefix: Course prefix (e.g., "INFO", "BUSN")
    
    Returns:
        str: URL like "https://bulletin.vcu.edu/azcourses/info/"
    """
    prefix_lower = prefix.lower()
    return f"https://bulletin.vcu.edu/azcourses/{prefix_lower}/"


# ============================================================================
# HTML Parsing and Data Extraction
# ============================================================================

def extract_course_paragraph(soup, prefix, number):
    """
    Extract the full course paragraph from bulletin HTML.
    
    Args:
        soup: BeautifulSoup object of the bulletin page
        prefix: Course prefix (e.g., "INFO")
        number: Course number (e.g., "370")
    
    Returns:
        str or None: Full paragraph text or None if not found
    """
    # Find the course heading: <strong>INFO 370. Course Title. 3 Hours.</strong>
    course_pattern = re.compile(rf'{prefix}\s+{number}\.', re.IGNORECASE)
    course_heading = soup.find('strong', string=course_pattern)
    
    if not course_heading:
        return None
    
    # The course info is split across two paragraphs:
    # 1. Parent <p> contains the heading
    # 2. Next sibling <p> contains the details (credits, prerequisites, description)
    heading_paragraph = course_heading.find_parent('p')
    
    if not heading_paragraph:
        return None
    
    # Get the heading text
    heading_text = heading_paragraph.get_text(strip=True)
    
    # Get the next sibling paragraph with the details
    details_paragraph = heading_paragraph.find_next_sibling('p')
    
    if details_paragraph:
        details_text = details_paragraph.get_text(strip=True)
        # Combine both paragraphs
        return heading_text + " " + details_text
    else:
        # If no sibling, just return the heading (edge case)
        return heading_text


def parse_course_paragraph(paragraph_text, prefix, number):
    """
    Parse the full course paragraph to extract components.
    
    Args:
        paragraph_text: Full text from bulletin
        prefix: Course prefix for validation
        number: Course number for validation
    
    Returns:
        dict: {
            'full_paragraph': 'Complete text...',
            'title': 'Course Title',
            'credits': '3',
            'prerequisites': 'MATH 211...' or 'None' or None,
            'description': 'Course description text...' or None
        }
    """
    result = {
        'full_paragraph': paragraph_text,
        'title': None,
        'credits': None,
        'prerequisites': None,
        'description': None
    }
    
    # Extract title (between course code and "Hours")
    title_pattern = rf'{prefix}\s+{number}\.\s+(.*?)\.\s+\d+\s+Hours?\.'
    title_match = re.search(title_pattern, paragraph_text, re.IGNORECASE)
    if title_match:
        result['title'] = title_match.group(1).strip()
    
    # Extract credits
    credits_pattern = r'(\d+)\s+credits?'
    credits_match = re.search(credits_pattern, paragraph_text, re.IGNORECASE)
    if credits_match:
        result['credits'] = credits_match.group(1)
    
    # Extract prerequisites
    # Look for "Prerequisite:" or "Prerequisites:" followed by text until we hit description
    prereq_patterns = [
        r'Prerequisites?:\s*([^.]+(?:\.[^.]+)?)',  # Match until description starts
        r'Prereq:\s*([^.]+)',
    ]
    
    for pattern in prereq_patterns:
        prereq_match = re.search(pattern, paragraph_text, re.IGNORECASE)
        if prereq_match:
            prereq_text = prereq_match.group(1).strip()
            # Stop at enrollment restrictions or actual description
            # Description typically starts after metadata
            result['prerequisites'] = prereq_text
            break
    
    # Check for "no prerequisites"
    if re.search(r'(none|no\s+prerequisites?)', paragraph_text, re.IGNORECASE):
        result['prerequisites'] = 'None'
    
    # Extract description
    # Description typically comes after metadata (semester, credits, prereqs, enrollment)
    # Look for sentences that don't match metadata patterns
    # Strategy: Split by '. ' and find where actual description starts
    
    # Remove the heading part first
    desc_text = paragraph_text
    heading_pattern = rf'{prefix}\s+{number}\.[^.]+\.\s+\d+\s+Hours?\.'
    desc_text = re.sub(heading_pattern, '', desc_text, flags=re.IGNORECASE)
    
    # Remove common metadata patterns
    metadata_patterns = [
        r'Semester course;[^.]+\.',
        r'\d+\s+lecture\s+hours[^.]+\.',
        r'\d+\s+credits?\.',
        r'Prerequisites?:[^.]+\.',
        r'Prereq:[^.]+\.',
        r'Enrollment\s+is\s+restricted[^.]+\.',
    ]
    
    for pattern in metadata_patterns:
        desc_text = re.sub(pattern, '', desc_text, flags=re.IGNORECASE)
    
    # What's left should be the description
    desc_text = desc_text.strip()
    
    # Description should be substantial (at least 50 characters)
    if len(desc_text) >= 50:
        result['description'] = desc_text
    
    return result


# ============================================================================
# Main Scraping Function
# ============================================================================

def scrape_course_data(prefix, number, use_cache=True):
    """
    Scrape course data from VCU Bulletin.
    
    Args:
        prefix: Course prefix (e.g., "INFO")
        number: Course number (e.g., "370")
        use_cache: Whether to use cached data if available
    
    Returns:
        dict: {
            'found': True/False,
            'full_paragraph': 'Complete bulletin text...',
            'description': 'Course description only...',
            'prerequisites': 'MATH 211...' or 'None',
            'title': 'Course Title',
            'credits': '3',
            'error': 'Error message if any'
        }
    """
    course_key = f"{prefix}_{number}"
    
    # Check cache first
    if use_cache:
        cached_data = _bulletin_cache.get(course_key)
        if cached_data:
            return cached_data
    
    result = {
        'found': False,
        'full_paragraph': None,
        'description': None,
        'prerequisites': None,
        'title': None,
        'credits': None,
        'error': None
    }
    
    try:
        # Build URL
        url = build_bulletin_url(prefix)
        
        # Make request with timeout
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.text, 'lxml')
        
        # Extract course paragraph
        paragraph = extract_course_paragraph(soup, prefix, number)
        
        if not paragraph:
            result['error'] = f"Course {prefix} {number} not found in bulletin"
            _bulletin_cache.set(course_key, result)
            return result
        
        # Parse the paragraph
        parsed_data = parse_course_paragraph(paragraph, prefix, number)
        
        result.update(parsed_data)
        result['found'] = True
        
        # Cache the successful result
        _bulletin_cache.set(course_key, result)
        
        # Rate limiting: be nice to VCU servers
        time.sleep(0.5)
        
        return result
        
    except requests.exceptions.Timeout:
        result['error'] = "Request timed out - VCU Bulletin server not responding"
        return result
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            result['error'] = f"URL not found - bulletin structure may have changed: {url}"
        else:
            result['error'] = f"HTTP error {e.response.status_code}: {str(e)}"
        return result
    
    except requests.exceptions.RequestException as e:
        result['error'] = f"Network error: {str(e)}"
        return result
    
    except Exception as e:
        result['error'] = f"Parsing error: {str(e)}"
        return result


# ============================================================================
# Utility Functions
# ============================================================================

def clear_cache():
    """Clear the bulletin cache"""
    _bulletin_cache.clear()


def get_cache_stats():
    """Get cache statistics for monitoring"""
    return {
        'entries': len(_bulletin_cache.cache),
        'courses': list(_bulletin_cache.cache.keys())
    }


# ============================================================================
# Testing / Debug
# ============================================================================

if __name__ == '__main__':
    # Test the scraper
    print("Testing VCU Bulletin Scraper...")
    print("=" * 60)
    
    # Test course: INFO 370
    result = scrape_course_data('INFO', '370')
    
    print(f"Course Found: {result['found']}")
    print(f"Title: {result['title']}")
    print(f"Credits: {result['credits']}")
    print(f"Prerequisites: {result['prerequisites']}")
    print(f"\nDescription:\n{result['description']}")
    print(f"\nFull Paragraph:\n{result['full_paragraph'][:200]}...")
    
    if result['error']:
        print(f"\nError: {result['error']}")
