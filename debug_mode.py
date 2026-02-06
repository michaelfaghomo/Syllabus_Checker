#!/usr/bin/env python3
"""
Debug mode for testing syllabi and viewing detailed detection information
Usage: python3 debug_mode.py <syllabus_file>
"""

import sys
import os
from syllabus_checker import SyllabusChecker
import json

def print_section(title, char='='):
    """Print a formatted section header"""
    print(f"\n{char * 60}")
    print(f" {title}")
    print(f"{char * 60}\n")

def debug_syllabus(filepath):
    """Run syllabus check with detailed debugging output"""
    
    if not os.path.exists(filepath):
        print(f"❌ Error: File not found: {filepath}")
        return
    
    print_section("VCU SYLLABUS CHECKER - DEBUG MODE", '=')

    print(f"File: {filepath}")
    print(f"Size: {os.path.getsize(filepath):,} bytes")

    
    # Initialize checker
    checker = SyllabusChecker()
    
    # Extract text
    print_section("Extracting Text", '-')
    try:
        text = checker.extract_text(filepath)

        print(f"Successfully extracted {len(text):,} characters")
        print(f"First 200 characters:")
        print(f"   {text[:200].replace(chr(10), ' ')[:200]}...")
    except Exception as e:
        print(f"Error extracting text: {e}")

    
    # Extract URLs
    print_section("Extracting URLs", '-')
    urls = checker.extract_urls(text)
    print(f"Found {len(urls)} URLs:")

    for i, url in enumerate(urls[:10], 1):  # Show first 10
        print(f"   {i}. {url}")
    if len(urls) > 10:
        print(f"   ... and {len(urls) - 10} more")
    
    # Check requirements
    print_section("Checking Requirements", '-')
    results = checker.check_syllabus(filepath)
    
    if 'error' in results:
        print(f"❌ Error: {results['error']}")
        return
    
    # Overall summary
    print_section("Overall Summary", '=')
    print(f"Required Items Found: {results['required']['found']}/{results['required']['total']}")
    print(f"Compliance Score: {results['required']['percentage']}%")
    print(f"Recommended Items: {results['recommended']['found']}/{results['recommended']['total']}")
    
    # Detailed required items
    print_section("Required Items - Detailed Breakdown", '=')
    for item in results['required']['items']:
        status = "[PASS]" if item['found'] else "[FAIL]"
        confidence_bar = "|" * int(item['confidence'] / 5) + "." * (20 - int(item['confidence'] / 5))
        
        print(f"\n{status} {item['name']}")
        print(f"   Confidence: [{confidence_bar}] {item['confidence']}%")
        
        if item.get('details'):
            print(f"   Matches found:")
            for detail in item['details']:
                # Sanitize detail string
                sanitized = detail.encode('ascii', 'ignore').decode('ascii')
                print(f"      - {sanitized}")
        else:
            if not item['found']:
                print(f"     Not detected - consider adding clearer labels")
    
    # Detailed recommended items
    print_section("Recommended Items - Detailed Breakdown", '=')
    for item in results['recommended']['items']:
        status = "[PASS]" if item['found'] else "[FAIL]"
        confidence_bar = "|" * int(item['confidence'] / 5) + "." * (20 - int(item['confidence'] / 5))
        
        print(f"\n{status} {item['name']}")
        print(f"   Confidence: [{confidence_bar}] {item['confidence']}%")
        
        if item.get('details'):
            print(f"   Matches found:")
            for detail in item['details']:
                # Sanitize detail string
                sanitized = detail.encode('ascii', 'ignore').decode('ascii')
                print(f"      - {sanitized}")
    
    # Recommendations
    print_section("Recommendations", '=')
    
    missing_required = [item for item in results['required']['items'] if not item['found']]
    low_confidence = [item for item in results['required']['items'] if item['found'] and item['confidence'] < 60]
    
    if missing_required:
        print("Missing Required Items:")
        for item in missing_required:
            print(f"   - {item['name']}")
            print(f"     Add this section with a clear header or keywords")
    
    if low_confidence:
        print("\nLow Confidence Items (may need clearer formatting):")
        for item in low_confidence:
            print(f"   - {item['name']} ({item['confidence']}%)")
            print(f"     Consider using clearer section headers")
    
    if not missing_required and not low_confidence:
        print("Excellent! All required items are clearly present!")
    
    # URL Check
    print_section("URL Verification", '=')
    
    # Check for VCU Provost link
    has_provost = any('provost' in url.lower() for url in urls)
    print(f"{'Found' if has_provost else 'Not Found'} VCU Provost/Syllabus Policy Link")
    if has_provost:
        provost_urls = [url for url in urls if 'provost' in url.lower()]
        print(f"   Found: {provost_urls[0]}")
    else:
        print(f"     Add: Link to VCU Syllabus Policy Statements")
    
    # Check for VCU Library link
    has_library = any('library.vcu.edu' in url.lower() for url in urls)
    print(f"\n{'Found' if has_library else 'Not Found'} VCU Libraries Link")
    if has_library:
        library_urls = [url for url in urls if 'library.vcu.edu' in url.lower()]
        print(f"   Found: {library_urls[0]}")
    else:
        print(f"     Add: https://www.library.vcu.edu/")
    
    print_section("Debug Complete", '=')
    print(f"To save these results, redirect output:")
    print(f"   python3 debug_mode.py {filepath} > results.txt")
    print()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 debug_mode.py <syllabus_file>")
        print("\nExample:")
        print("  python3 debug_mode.py test_samples/my_syllabus.pdf")
        print("  python3 debug_mode.py path/to/syllabus.docx")
        sys.exit(1)
    
    filepath = sys.argv[1]
    debug_syllabus(filepath)
