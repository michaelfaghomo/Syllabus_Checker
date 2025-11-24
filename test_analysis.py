#!/usr/bin/env python3
"""
Comprehensive test analysis for syllabus checker
Runs all test samples and generates improvement recommendations
"""

import os
import sys
import json
from syllabus_checker import SyllabusChecker
from datetime import datetime

def print_separator(char='=', length=80):
    """Print a separator line"""
    print(char * length)

def analyze_requirement(item, req_name):
    """Analyze a single requirement result"""
    return {
        'name': req_name,
        'found': item['found'],
        'confidence': item['confidence'],
        'details': item.get('details', []),
        'status': 'PASS' if item['found'] else 'FAIL'
    }

def analyze_syllabus(filepath, checker):
    """Analyze a single syllabus file"""
    print(f"\n{'='*80}")
    print(f"ANALYZING: {os.path.basename(filepath)}")
    print(f"{'='*80}\n")
    
    if not os.path.exists(filepath):
        return None
    
    # Extract text
    try:
        text = checker.extract_text(filepath)
        print(f"[OK] Text extracted: {len(text):,} characters")
    except Exception as e:
        print(f"[ERROR] Error extracting text: {e}")
        return None
    
    # Extract URLs
    urls = checker.extract_urls(text)
    print(f"[OK] URLs found: {len(urls)}")
    
    # Check syllabus
    results = checker.check_syllabus(filepath)
    
    if 'error' in results:
        print(f"✗ Error checking syllabus: {results['error']}")
        return None
    
    # Analyze results
    analysis = {
        'filename': os.path.basename(filepath),
        'text_length': len(text),
        'urls_count': len(urls),
        'urls': urls,
        'score': results['required']['percentage'],
        'required_found': results['required']['found'],
        'required_total': results['required']['total'],
        'recommended_found': results['recommended']['found'],
        'recommended_total': results['recommended']['total'],
        'required_items': [],
        'recommended_items': [],
        'missing_required': [],
        'low_confidence': [],
        'false_negatives': []
    }
    
    # Analyze required items
    for item in results['required']['items']:
        req_analysis = analyze_requirement(item, item['name'])
        analysis['required_items'].append(req_analysis)
        
        if not item['found']:
            analysis['missing_required'].append(req_analysis)
        elif item['confidence'] < 60:
            analysis['low_confidence'].append(req_analysis)
    
    # Analyze recommended items
    for item in results['recommended']['items']:
        rec_analysis = analyze_requirement(item, item['name'])
        analysis['recommended_items'].append(rec_analysis)
    
    # Print summary
    print(f"\n{'-'*80}")
    print(f"SCORE: {analysis['score']}% ({analysis['required_found']}/{analysis['required_total']} required)")
    if analysis['score'] >= 90:
        print(f"Status: [PASS]")
    elif analysis['score'] >= 70:
        print(f"Status: [NEEDS WORK]")
    else:
        print(f"Status: [FAIL]")
    print(f"{'-'*80}\n")
    
    # Print missing required items
    if analysis['missing_required']:
        print("[X] MISSING REQUIRED ITEMS:")
        for item in analysis['missing_required']:
            print(f"  - {item['name']} (confidence: {item['confidence']}%)")
    
    # Print low confidence items
    if analysis['low_confidence']:
        print("\n[!] LOW CONFIDENCE ITEMS (may be false positives):")
        for item in analysis['low_confidence']:
            print(f"  - {item['name']} (confidence: {item['confidence']}%)")
    
    # Check for obvious issues
    print("\nDETAILED ANALYSIS:")
    
    # Check for VCU links
    has_provost = any('provost' in url.lower() or 'syllabus' in url.lower() for url in urls)
    has_library = any('library.vcu.edu' in url.lower() for url in urls)
    
    print(f"  VCU Provost Link: {'Found' if has_provost else 'Not Found'}")
    print(f"  VCU Library Link: {'Found' if has_library else 'Not Found'}")
    
    # Analyze text for common patterns
    text_lower = text.lower()
    print(f"\n  Pattern Analysis:")
    print(f"    - Contains 'prerequisite': {('prerequisite' in text_lower or 'prereq' in text_lower)}")
    print(f"    - Contains 'learning outcome': {'learning outcome' in text_lower}")
    print(f"    - Contains 'grading scale': {'grading scale' in text_lower}")
    print(f"    - Contains course schedule keywords: {'week' in text_lower and 'topic' in text_lower}")
    print(f"    - Contains grade weights (%): {bool(len([c for c in text if c == '%']) > 3)}")
    
    return analysis

def generate_report(all_analyses):
    """Generate comprehensive improvement report"""
    print(f"\n\n{'='*80}")
    print("COMPREHENSIVE ANALYSIS REPORT")
    print(f"{'='*80}\n")
    
    total_files = len(all_analyses)
    avg_score = sum(a['score'] for a in all_analyses) / total_files if total_files > 0 else 0
    
    print(f"Total Files Analyzed: {total_files}")
    print(f"Average Score: {avg_score:.1f}%\n")
    
    # Aggregate missing items across all files
    missing_counts = {}
    for analysis in all_analyses:
        for item in analysis['missing_required']:
            name = item['name']
            if name not in missing_counts:
                missing_counts[name] = {
                    'count': 0,
                    'files': [],
                    'avg_confidence': []
                }
            missing_counts[name]['count'] += 1
            missing_counts[name]['files'].append(analysis['filename'])
            missing_counts[name]['avg_confidence'].append(item['confidence'])
    
    # Aggregate low confidence items
    low_conf_counts = {}
    for analysis in all_analyses:
        for item in analysis['low_confidence']:
            name = item['name']
            if name not in low_conf_counts:
                low_conf_counts[name] = {
                    'count': 0,
                    'files': [],
                    'confidences': []
                }
            low_conf_counts[name]['count'] += 1
            low_conf_counts[name]['files'].append(analysis['filename'])
            low_conf_counts[name]['confidences'].append(item['confidence'])
    
    # Print most commonly missing items
    if missing_counts:
        print(f"\n{'='*80}")
        print("MOST COMMONLY MISSING REQUIRED ITEMS:")
        print(f"{'='*80}\n")
        
        sorted_missing = sorted(missing_counts.items(), key=lambda x: x[1]['count'], reverse=True)
        for name, data in sorted_missing:
            avg_conf = sum(data['avg_confidence']) / len(data['avg_confidence'])
            print(f"\n[X] {name}")
            print(f"   Missing in {data['count']}/{total_files} files ({data['count']/total_files*100:.0f}%)")
            print(f"   Average confidence when checked: {avg_conf:.1f}%")
            print(f"   Files: {', '.join(data['files'])}")
    
    # Print low confidence items
    if low_conf_counts:
        print(f"\n\n{'='*80}")
        print("ITEMS WITH LOW CONFIDENCE (Possible False Positives):")
        print(f"{'='*80}\n")
        
        sorted_low_conf = sorted(low_conf_counts.items(), key=lambda x: x[1]['count'], reverse=True)
        for name, data in sorted_low_conf:
            avg_conf = sum(data['confidences']) / len(data['confidences'])
            print(f"\n[!] {name}")
            print(f"   Low confidence in {data['count']}/{total_files} files")
            print(f"   Average confidence: {avg_conf:.1f}%")
            print(f"   Files: {', '.join(data['files'])}")
    
    # Generate improvement recommendations
    print(f"\n\n{'='*80}")
    print("ALGORITHM IMPROVEMENT RECOMMENDATIONS")
    print(f"{'='*80}\n")
    
    recommendations = []
    
    # Analyze missing items for patterns
    for name, data in missing_counts.items():
        if data['count'] >= total_files * 0.5:  # Missing in 50%+ of files
            avg_conf = sum(data['avg_confidence']) / len(data['avg_confidence'])
            if avg_conf < 25:
                recommendations.append({
                    'priority': 'HIGH',
                    'item': name,
                    'issue': f'Frequently missed (in {data["count"]}/{total_files} files) with very low confidence ({avg_conf:.1f}%)',
                    'suggestion': 'Add more flexible patterns, check for alternative phrasings, consider context-aware detection'
                })
            elif avg_conf < 40:
                recommendations.append({
                    'priority': 'MEDIUM',
                    'item': name,
                    'issue': f'Frequently missed (in {data["count"]}/{total_files} files) with low confidence ({avg_conf:.1f}%)',
                    'suggestion': 'Review existing patterns, add edge cases, improve confidence scoring'
                })
    
    # Analyze low confidence items
    for name, data in low_conf_counts.items():
        if data['count'] >= total_files * 0.5:  # Low conf in 50%+ of files
            avg_conf = sum(data['confidences']) / len(data['confidences'])
            recommendations.append({
                'priority': 'MEDIUM',
                'item': name,
                'issue': f'Detected with low confidence in {data["count"]}/{total_files} files (avg: {avg_conf:.1f}%)',
                'suggestion': 'Strengthen primary patterns, add more specific keywords, increase min_matches threshold'
            })
    
    # Sort and print recommendations
    recommendations.sort(key=lambda x: (0 if x['priority'] == 'HIGH' else 1, x['item']))
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. [{rec['priority']}] {rec['item']}")
            print(f"   Issue: {rec['issue']}")
            print(f"   Suggestion: {rec['suggestion']}\n")
    else:
        print("[OK] No major issues detected! Algorithm is performing well.\n")
    
    # URL analysis
    print(f"\n{'='*80}")
    print("URL DETECTION ANALYSIS")
    print(f"{'='*80}\n")
    
    total_urls = sum(a['urls_count'] for a in all_analyses)
    print(f"Total URLs found across all files: {total_urls}")
    
    for analysis in all_analyses:
        print(f"\n{analysis['filename']}: {analysis['urls_count']} URLs")
        if analysis['urls']:
            for url in analysis['urls'][:5]:  # Show first 5
                print(f"  - {url[:70]}{'...' if len(url) > 70 else ''}")
            if len(analysis['urls']) > 5:
                print(f"  ... and {len(analysis['urls']) - 5} more")
    
    return recommendations

def save_json_report(all_analyses, recommendations, output_file='test_analysis_report.json'):
    """Save detailed JSON report"""
    report = {
        'timestamp': datetime.now().isoformat(),
        'summary': {
            'total_files': len(all_analyses),
            'average_score': sum(a['score'] for a in all_analyses) / len(all_analyses) if all_analyses else 0,
            'total_recommendations': len(recommendations)
        },
        'analyses': all_analyses,
        'recommendations': recommendations
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n\n[SAVED] Detailed JSON report saved to: {output_file}")

def main():
    """Main test execution"""
    print(f"{'='*80}")
    print("VCU SYLLABUS CHECKER - COMPREHENSIVE TEST ANALYSIS")
    print(f"{'='*80}")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Initialize checker
    checker = SyllabusChecker()
    
    # Find test samples
    test_dir = 'test_samples'
    if not os.path.exists(test_dir):
        print(f"Error: {test_dir} directory not found")
        return
    
    # Get all test files
    test_files = []
    for file in os.listdir(test_dir):
        if file.lower().endswith(('.pdf', '.docx', '.txt')):
            test_files.append(os.path.join(test_dir, file))
    
    if not test_files:
        print(f"No test files found in {test_dir}")
        return
    
    print(f"Found {len(test_files)} test file(s):\n")
    for f in test_files:
        print(f"  - {os.path.basename(f)}")
    
    # Analyze each file
    all_analyses = []
    for filepath in test_files:
        analysis = analyze_syllabus(filepath, checker)
        if analysis:
            all_analyses.append(analysis)
    
    # Generate comprehensive report
    if all_analyses:
        recommendations = generate_report(all_analyses)
        
        # Save JSON report
        save_json_report(all_analyses, recommendations)
        
        print(f"\n{'='*80}")
        print("[OK] ANALYSIS COMPLETE")
        print(f"{'='*80}\n")
    else:
        print("\n[ERROR] No successful analyses completed")

if __name__ == '__main__':
    main()

