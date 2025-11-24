# Algorithm Improvement Recommendations

**Based on Testing:** 3 Real VCU Syllabi  
**Test Date:** November 24, 2025  
**Average Score:** 78.6% (11.7/14 required items found)

---

## Executive Summary

After testing the syllabus checker on 3 real VCU syllabi, the algorithm achieves an average detection rate of **78.6%** for required items. While this is good, there are clear opportunities for improvement, particularly in:

1. **Course Identification** - Low confidence (39.3% avg) across all files
2. **Grade Categories & Weights** - Missed in 67% of files
3. **Course Schedule** - Missed in 67% of files
4. **VCU Libraries Link** - Low confidence (40% avg) when detected

---

## Test Results Summary

### File-by-File Scores
| File | Score | Found | Issues |
|------|-------|-------|--------|
| BUSN 301 FA25 Maynard.docx | 71.4% | 10/14 | Missing: final exam, grading scale, grade weights, library link |
| INFO 370 Fall 2025 syllabus.pdf | 78.6% | 11/14 | Missing: course description, schedule, grade weights |
| MGMT303.904_RINP_Custodio_Fall25.08.07.25-Syllabus.pdf | 85.7% | 12/14 | Missing: learning outcomes, schedule |

### Most Common Problems

**Items Missing in 2+ Files:**
- **Grade categories and weights** (67% failure rate)
- **Course schedule** (67% failure rate)

**Items with Low Confidence (all files):**
- **Course prefix and number** (39.3% avg confidence)
- **Prerequisites** (40% avg confidence)
- **Final exam** (42.5% avg confidence)
- **VCU Libraries link** (40% avg confidence)

---

## Detailed Improvement Recommendations

### 🔴 HIGH PRIORITY

#### 1. Grade Categories and Weights Detection
**Current Issue:** Missed in 2/3 files (67%), very low confidence (34%)

**Problem Analysis:**
- Current pattern requires 3+ matches of `\d+\s*%`
- Some syllabi use tables/grids for grade breakdown
- Text extraction from PDFs may not preserve table structure
- Pattern may be too strict for edge cases

**Proposed Improvements:**

```python
'grade_weights': {
    'name': 'Grade categories and weights',
    'primary_patterns': [
        r'\d+\s*%',  # Percentage
        r'(?i)(?:weight|weigh)s?\s*:?',
        r'(?i)(?:exam|quiz|homework|assignment|project|participation|attendance)s?\s*[:=]?\s*\d+\s*%',
        r'(?i)grade\s+(?:breakdown|composition|distribution)\s*:?',
        r'(?i)(?:worth|counts?\s+(?:for|as))\s+\d+\s*%',
        # NEW PATTERNS:
        r'(?i)(?:exam|quiz|test)s?\s+\d+%',  # "Exams 40%"
        r'(?i)(?:total|sum)\s+(?:points|pts)',  # Point-based systems
        r'\d+\s*(?:points|pts)\s*(?:each|total)',  # "100 points each"
        r'(?i)(?:grading|grade)\s+(?:policy|breakdown|criteria)',  # Alternative headers
    ],
    'context_keywords': ['weight', 'percent', 'breakdown', 'distribution', 'points', 'grade', 'evaluation'],
    'min_matches': 2,  # REDUCED from 3
    'flexible_scoring': True  # NEW: Allow point systems without percentages
}
```

**Rationale:** Reduce min_matches from 3 to 2 to catch edge cases, add patterns for point-based grading systems.

---

#### 2. Course Schedule Detection
**Current Issue:** Missed in 2/3 files (67%), confidence 46%

**Problem Analysis:**
- Requires 2+ matches for weekly content
- Some syllabi use "Module" instead of "Week"
- Schedule may be in a separate document (not detected)
- Date-based schedules without "Week X" labels not caught

**Proposed Improvements:**

```python
'course_schedule': {
    'name': 'Course schedule',
    'primary_patterns': [
        r'(?i)(?:course|class|weekly|tentative)\s*schedule\s*:?',
        r'(?i)week\s+\d+\s*:?',
        r'(?i)(?:calendar|timeline)\s*:?',
        r'(?i)(?:week|session|class)\s+\d+.*(?:topic|chapter)',
        r'(?i)(?:date|dates?)\s+(?:topic|chapter|reading)',
        # NEW PATTERNS:
        r'(?i)module\s+\d+\s*:?',  # "Module 1: Introduction"
        r'(?i)(?:lesson|unit)\s+\d+',  # "Lesson 1", "Unit 1"
        r'(?i)(?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d+.*(?:topic|chapter|reading)',  # Date-based
        r'(?i)\d{1,2}/\d{1,2}.*(?:topic|chapter|assignment)',  # "9/1 - Topic: Intro"
        r'(?i)(?:see|refer to|attached)\s+(?:schedule|calendar)',  # References to external schedule
    ],
    'context_keywords': ['schedule', 'week', 'calendar', 'topic', 'date', 'module', 'lesson', 'unit'],
    'min_matches': 1,  # REDUCED from 2 - any clear schedule indicator
    'detect_external_ref': True  # NEW: Detect references to separate schedules
}
```

**Rationale:** Many syllabi use "Module" or date-based schedules instead of "Week". Also detect references to external schedules.

---

### 🟡 MEDIUM PRIORITY

#### 3. Course Prefix and Number Detection
**Current Issue:** Low confidence in ALL files (39.3% avg)

**Problem Analysis:**
- Pattern `\b[A-Z]{2,4}\s*-?\s*\d{3,4}` only gets 1 match
- Low context keyword matches
- Confidence calculation penalizes single pattern matches

**Current Confidence Issue:**
```python
# Current scoring gives only 30% for 1 match
pattern_score = matches * 30  # 1 * 30 = 30%
context_score = (context_matches / total_keywords * 20)  # ~8%
# Total: ~38-42%
```

**Proposed Improvements:**

```python
'course_info': {
    'name': 'Course prefix and number, section number, and title',
    'primary_patterns': [
        r'\b[A-Z]{2,4}\s*-?\s*\d{3,4}',  # BIOL 3001, CHEM-2001
        r'(?i)section\s*:?\s*#?\s*\d+',  # Section: 001, Section #1
        # NEW PATTERNS:
        r'\b[A-Z]{2,4}\s+\d{3,4}\s*-\s*\d{3}',  # "MGMT 303-904" (section in same pattern)
        r'(?i)course\s*(?:code|number)\s*:?\s*[A-Z]{2,4}',  # "Course Code: BUSN"
        r'\b[A-Z]{2,4}\s+\d{3,4}\s*/\s*[A-Z]{2,4}\s+\d{3,4}',  # Cross-listed "BIOL 301/CHEM 301"
    ],
    'context_keywords': ['course', 'class', 'section', 'prefix', 'number', 'code'],
    'min_matches': 1,
    'boost_confidence': True,  # NEW: This is a critical identifier, boost confidence if found
    'confidence_boost': 30  # NEW: Add 30% to confidence if course code detected
}
```

**Alternative Fix - Adjust Confidence Calculation:**
```python
# For 'course_info', give higher weight to pattern match
if requirement_key == 'course_info' and matches >= 1:
    pattern_score = 60  # Boosted from 30
    # Course code is highly distinctive, so strong match = high confidence
```

**Rationale:** Course codes are highly distinctive. If we find "BUSN 301", it's almost certainly the course info. Confidence should be higher.

---

#### 4. Course Prerequisites Detection
**Current Issue:** Low confidence in 2/3 files (40% avg)

**Problem Analysis:**
- Pattern matches "required courses" which is vague
- May match other "required" content
- Actual text check shows one file doesn't have "prerequisite" keyword

**Proposed Improvements:**

```python
'prerequisites': {
    'name': 'Course prerequisites',
    'primary_patterns': [
        r'(?i)prerequisite\s*:?',
        r'(?i)prereq\s*:?',
        r'(?i)required\s+courses?\s*:?',
        r'(?i)(?:none|no\s+prerequisites)',  # Also detect when there are none
        r'(?i)students?\s+must\s+have\s+(?:completed|taken)',
        # NEW PATTERNS:
        r'(?i)pre-req\s*:?',  # Hyphenated version
        r'(?i)prerequisite(?:s)?:\s*(?:none|[A-Z]{2,4}\s+\d{3,4})',  # Explicit format
        r'(?i)admission\s+(?:to|requirement)',  # "Admission to program required"
        r'(?i)completion\s+of\s+[A-Z]{2,4}\s+\d{3,4}',  # "Completion of MATH 101"
        r'(?i)junior\s+(?:or\s+)?senior\s+standing',  # Class level requirements
    ],
    'context_keywords': ['prerequisite', 'prereq', 'pre-req', 'required', 'prior', 'before', 'admission', 'standing'],
    'min_matches': 1,
    'allow_none_statement': True,  # NEW: "No prerequisites" is a valid match
    'confidence_boost_for_explicit': 20  # NEW: Boost if explicit course codes listed
}
```

**Rationale:** Some syllabi state "None" for prerequisites, which should still count as addressing the requirement.

---

#### 5. VCU Libraries Statement Detection
**Current Issue:** Low confidence in 2/3 files (40%), missed entirely in 1/3 files

**Problem Analysis:**
- Requires library.vcu.edu URL AND specific text
- Text may be paraphrased
- URL might not be extracted properly from some PDFs

**Proposed Improvements:**

```python
'library_statement': {
    'name': 'VCU Libraries statement and link',
    'url_patterns': [
        r'https?://(?:www\.)?library\.vcu\.edu',
        r'https?://[^\s]*vcu\.edu[^\s]*library',
        # NEW:
        r'library\.vcu\.edu',  # Without http:// prefix
    ],
    'text_patterns': [
        r'(?i)vcu\s+libraries?',
        r'(?i)use\s+vcu\s+libraries?',
        r'(?i)library\s+resources',
        r'(?i)libraries?\s+(?:to\s+)?find\s+and\s+access',
        r'(?i)library.*?(?:resources|services|support)',
        # NEW PATTERNS:
        r'(?i)vcu\s+libraries?\s+(?:provides?|offers?)',
        r'(?i)access\s+(?:the\s+)?library\s+(?:at|through)',
        r'(?i)library\s+support\s+(?:for|to)',
    ],
    'required_phrases': [
        r'(?i)vcu\s+libraries',  # Must mention VCU Libraries
        # RELAXED: Removed strict URL requirement - can be implied
    ],
    'context_keywords': ['library', 'libraries', 'vcu', 'resources', 'access', 'research'],
    'min_matches': 1,  # REDUCED from 2
    'check_urls': True,
    'url_bonus_value': 40  # INCREASED from 20 - URL is strong indicator
}
```

**Rationale:** Some syllabi mention the library without the full statement. Focus on URL detection as primary indicator.

---

#### 6. Final Exam Detection
**Current Issue:** Low confidence in 2/3 files (42.5%), missed in 1 file (10%)

**Problem Analysis:**
- Some courses have projects instead of exams
- "TBA" or "See university schedule" not being detected
- Alternative assessments not recognized

**Proposed Improvements:**

```python
'final_exam': {
    'name': 'Final exam date and time',
    'primary_patterns': [
        r'(?i)final\s+exam\s*:?',
        r'(?i)final\s+assessment\s*:?',
        r'(?i)final\s+examination\s*:?',
        r'(?i)(?:final|exam)\s+(?:date|time|schedule)',
        r'(?i)(?:no\s+final\s+exam|final\s+project\s+instead)',
        # NEW PATTERNS:
        r'(?i)final\s+exam:\s*(?:TBA|TBD|see\s+schedule)',  # "Final Exam: TBA"
        r'(?i)refer\s+to\s+(?:university|vcu)\s+final\s+exam\s+schedule',
        r'(?i)(?:cumulative\s+)?final\s+(?:project|presentation|paper)',  # Alternative assessments
        r'(?i)final\s+assessment\s+date',
        r'(?i)exam\s+period:\s*(?:dec|december)',  # Date ranges
    ],
    'context_keywords': ['final', 'exam', 'examination', 'assessment', 'project', 'TBA', 'schedule'],
    'min_matches': 1,
    'recognize_alternatives': True,  # NEW: Projects count as finals
    'recognize_tba': True  # NEW: "TBA" counts as addressing requirement
}
```

**Rationale:** Mentioning a final exam even with "TBA" fulfills the requirement. Alternative final assessments should count.

---

### 🟢 LOW PRIORITY

#### 7. Student Learning Outcomes
**Current Issue:** Low confidence in 1/3 files (34%), missed in 1/3 files (12%)

**Current State:** Generally working well (detected in 2/3 files)

**Minor Improvement:**

```python
'learning_outcomes': {
    'name': 'Student learning outcomes',
    'primary_patterns': [
        r'(?i)learning\s*outcomes?\s*:?',
        r'(?i)course\s*objectives?\s*:?',
        r'(?i)(?:upon\s+completion|by\s+the\s+end).*students?\s+(?:will|should)',
        r'(?i)students?\s+will\s+be\s+able\s+to',
        r'(?i)learning\s+goals?\s*:?',
        # NEW PATTERNS:
        r'(?i)course\s+learning\s+outcomes',  # Explicit version
        r'(?i)student\s+learning\s+objectives',
        r'(?i)by\s+completing\s+this\s+course',
        r'(?i)successful\s+students?\s+will',
    ],
    'context_keywords': ['learning', 'outcome', 'objective', 'goal', 'students will', 'able to'],
    'min_matches': 1,
    'require_list': True  # NEW: Should have multiple items (list detection)
}
```

---

#### 8. University Course Description
**Current Issue:** Missed in 1/3 files (4% confidence)

**Current State:** Works in 2/3 files, one complete miss

**Proposed Improvement:**

```python
'course_description': {
    'name': 'University course description',
    'primary_patterns': [
        r'(?i)course\s*description\s*:?',
        r'(?i)description\s*:?\s*(?:this\s+course|students\s+will)',
        r'(?i)(?:this\s+course|the\s+course)\s+(?:provides|introduces|explores|examines|covers)',
        # NEW PATTERNS:
        r'(?i)catalog\s+description',  # "University Catalog Description"
        r'(?i)official\s+description',
        r'(?i)from\s+the\s+(?:university\s+)?bulletin',
        r'(?i)per\s+(?:the\s+)?(?:university\s+)?catalog',
    ],
    'context_keywords': ['description', 'course', 'covers', 'introduces', 'explores', 'catalog', 'bulletin'],
    'min_matches': 1,
    'min_text_length': 50,
    'detect_bulletin_ref': True  # NEW: Detect references to official descriptions
}
```

---

## Implementation Priority

### Phase 1 (Immediate) - Fix High-Impact Issues
1. ✅ **Grade Categories & Weights** - Reduce min_matches, add point-system patterns
2. ✅ **Course Schedule** - Add module/date patterns, reduce min_matches
3. ✅ **Course Prefix/Number** - Boost confidence scoring for strong matches

**Expected Impact:** +15-20% average score (from 78.6% to ~93-98%)

### Phase 2 (Short-term) - Improve Confidence Scores
4. ✅ **Prerequisites** - Add "None" detection, more patterns
5. ✅ **VCU Libraries** - Relax requirements, boost URL scoring
6. ✅ **Final Exam** - Recognize TBA and alternatives

**Expected Impact:** Reduce false negatives, increase average confidence from 40% to 60%+

### Phase 3 (Long-term) - Edge Cases
7. ✅ **Learning Outcomes** - List detection
8. ✅ **Course Description** - Bulletin references

---

## Testing Recommendations

### Create Test Suite
```python
# test_suite.py
test_cases = {
    'grade_weights_percentage': {
        'text': 'Exams 40%, Homework 30%, Final 30%',
        'should_detect': True
    },
    'grade_weights_points': {
        'text': 'Exams: 400 points, Homework: 300 points, Total: 1000 points',
        'should_detect': True
    },
    'schedule_modules': {
        'text': 'Module 1: Introduction to Management\nModule 2: Leadership',
        'should_detect': True
    },
    'prerequisites_none': {
        'text': 'Prerequisites: None',
        'should_detect': True
    },
    'final_exam_tba': {
        'text': 'Final Exam: TBA - See University Schedule',
        'should_detect': True
    }
}
```

### Validation Process
1. Apply improvements to `syllabus_checker.py`
2. Re-run `test_analysis.py` on existing samples
3. Verify improvements:
   - Average score should increase to 90%+
   - Low confidence items should improve to 50%+
4. Test on additional syllabi if available

---

## Specific Code Changes

### File: `syllabus_checker.py`

**Line 141-151: Grade categories and weights**
```python
# CURRENT
'grade_weights': {
    'min_matches': 3  # Too strict
}

# PROPOSED
'grade_weights': {
    'primary_patterns': [
        # ... existing patterns ...
        r'(?i)(?:exam|quiz|test)s?\s+\d+%',
        r'(?i)(?:total|sum)\s+(?:points|pts)',
        r'\d+\s*(?:points|pts)\s*(?:each|total)',
    ],
    'min_matches': 2  # Reduced from 3
}
```

**Line 103-114: Course schedule**
```python
# ADD new patterns
'primary_patterns': [
    # ... existing patterns ...
    r'(?i)module\s+\d+\s*:?',
    r'(?i)(?:lesson|unit)\s+\d+',
    r'(?i)\d{1,2}/\d{1,2}.*(?:topic|chapter|assignment)',
],
'min_matches': 1  # Reduced from 2
```

**Line 10-19: Course info confidence boost**
```python
# In check_requirement_enhanced() around line 376:
# ADD special handling for course_info
if requirement_key == 'course_info' and matches >= 1:
    confidence = min(100, confidence + 30)  # Boost confidence
```

---

## Expected Outcomes

| Metric | Before | After (Projected) |
|--------|--------|-------------------|
| Average Score | 78.6% | 93-98% |
| Grade Weights Detection | 33% | 90%+ |
| Course Schedule Detection | 33% | 85%+ |
| Course Prefix Confidence | 39% | 65%+ |
| VCU Libraries Confidence | 40% | 65%+ |

---

## Conclusion

The syllabus checker algorithm is **performing well** (78.6% average), but has clear improvement opportunities. The recommended changes focus on:

1. **Reducing overly strict thresholds** (min_matches: 3→2)
2. **Adding alternative patterns** (modules instead of weeks, points instead of percentages)
3. **Boosting confidence** for distinctive patterns (course codes)
4. **Recognizing valid alternatives** (TBA, None, alternative assessments)

These changes are **low-risk** and should significantly improve detection rates without increasing false positives.

---

**Next Step:** Implement Phase 1 changes and re-test on the same 3 syllabi to validate improvements.

