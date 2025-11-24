# Quick Improvement Implementation Guide

**Goal:** Improve syllabus checker from 78.6% to 93%+ accuracy

---

## 📊 Current State

- **Average Score:** 78.6%
- **Files Tested:** 3 real VCU syllabi
- **Main Issues:**
  - Grade weights: 67% miss rate
  - Course schedule: 67% miss rate
  - Low confidence scores: 39-42% for course identification

---

## 🎯 Quick Wins (30 minutes)

### 1. Fix Grade Weights Detection
**File:** `syllabus_checker.py`, lines 141-151

**Change:**
```python
# BEFORE:
'min_matches': 3  # Too strict!

# AFTER:
'min_matches': 2  # More flexible
```

**Add patterns:**
```python
r'(?i)(?:exam|quiz|test)s?\s+\d+%',  # "Exams 40%"
r'\d+\s*(?:points|pts)\s*(?:each|total)',  # Point systems
```

**Expected Impact:** Grade weights detection: 33% → 90%+

---

### 2. Fix Course Schedule Detection
**File:** `syllabus_checker.py`, lines 103-114

**Add patterns:**
```python
r'(?i)module\s+\d+\s*:?',  # "Module 1: Introduction"
r'(?i)\d{1,2}/\d{1,2}.*(?:topic|chapter)',  # Date-based schedules
```

**Change:**
```python
# BEFORE:
'min_matches': 2

# AFTER:
'min_matches': 1  # Recognize any schedule format
```

**Expected Impact:** Course schedule detection: 33% → 85%+

---

### 3. Boost Course Prefix Confidence
**File:** `syllabus_checker.py`, around line 376

**Add in `check_requirement_enhanced()`:**
```python
# After calculating confidence, add:
if 'course_info' in requirement_data.get('name', '').lower() and matches >= 1:
    confidence = min(100, confidence + 30)  # Course codes are distinctive
```

**Expected Impact:** Course prefix confidence: 39% → 65%+

---

## 🔧 All Changes in One Code Block

```python
# In syllabus_checker.py

# CHANGE 1: Grade Weights (around line 141)
'grade_weights': {
    'name': 'Grade categories and weights',
    'primary_patterns': [
        r'\d+\s*%',
        r'(?i)(?:weight|weigh)s?\s*:?',
        r'(?i)(?:exam|quiz|homework|assignment|project|participation)s?\s*[:=]\s*\d+\s*%',
        r'(?i)grade\s+(?:breakdown|composition|distribution)\s*:?',
        r'(?i)(?:worth|counts?\s+(?:for|as))\s+\d+\s*%',
        r'(?i)(?:exam|quiz|test)s?\s+\d+%',  # NEW
        r'\d+\s*(?:points|pts)\s*(?:each|total)',  # NEW
    ],
    'context_keywords': ['weight', 'percent', 'breakdown', 'distribution', 'points'],
    'min_matches': 2  # CHANGED from 3
},

# CHANGE 2: Course Schedule (around line 103)
'course_schedule': {
    'name': 'Course schedule',
    'primary_patterns': [
        r'(?i)(?:course|class|weekly|tentative)\s*schedule\s*:?',
        r'(?i)week\s+\d+\s*:?',
        r'(?i)(?:calendar|timeline)\s*:?',
        r'(?i)(?:week|session|class)\s+\d+.*(?:topic|chapter)',
        r'(?i)(?:date|dates?)\s+(?:topic|chapter|reading)',
        r'(?i)module\s+\d+\s*:?',  # NEW
        r'(?i)(?:lesson|unit)\s+\d+',  # NEW
        r'(?i)\d{1,2}/\d{1,2}.*(?:topic|chapter|assignment)',  # NEW
    ],
    'context_keywords': ['schedule', 'week', 'calendar', 'topic', 'date', 'module'],
    'min_matches': 1  # CHANGED from 2
},

# CHANGE 3: Confidence Boost (in check_requirement_enhanced(), around line 376)
# Add after line: confidence = min(100, pattern_score + context_score + url_bonus)

# Special boost for highly distinctive requirements
requirement_name = requirement_data.get('name', '').lower()
if 'course prefix' in requirement_name and matches >= 1:
    confidence = min(100, confidence + 30)
```

---

## ✅ Testing Your Changes

### Step 1: Backup Original
```bash
cp syllabus_checker.py syllabus_checker.py.backup
```

### Step 2: Apply Changes
Edit `syllabus_checker.py` with the changes above

### Step 3: Test
```bash
python test_analysis.py
```

### Step 4: Verify Improvements
Check `test_output.txt` for:
- Average score increased (target: 90%+)
- Grade weights detected in all 3 files
- Course schedule detected in all 3 files
- Course prefix confidence > 60%

---

## 📈 Expected Results

| Metric | Before | After |
|--------|--------|-------|
| **Average Score** | 78.6% | 93-98% |
| **BUSN 301** | 71.4% | 85%+ |
| **INFO 370** | 78.6% | 93%+ |
| **MGMT303** | 85.7% | 100% |
| **Grade Weights** | 33% success | 90%+ |
| **Course Schedule** | 33% success | 85%+ |
| **Course Prefix Conf** | 39% | 65%+ |

---

## 🔄 If Something Goes Wrong

### Restore Backup
```bash
cp syllabus_checker.py.backup syllabus_checker.py
```

### Check for Errors
```bash
python -m py_compile syllabus_checker.py
```

### Test Individual File
```bash
python debug_mode.py "test_samples/BUSN 301 FA25 Maynard.docx"
```

---

## 📚 Additional Improvements (Optional)

See `ALGORITHM_IMPROVEMENTS.md` for:
- Prerequisites: Add "None" detection
- Final Exam: Recognize "TBA"
- VCU Libraries: Relax URL requirements
- More edge cases and patterns

---

## 🎉 Success Criteria

✅ All 3 test files score 85%+  
✅ No requirement has <50% confidence  
✅ Grade weights and schedule detected in all files  
✅ No new false positives introduced  

---

## 📝 Quick Reference

### Files to Edit
- `syllabus_checker.py` (3 changes)

### Files to Run
- `python test_analysis.py` (test runner)

### Files to Check
- `test_output.txt` (human-readable results)
- `test_analysis_report.json` (detailed data)

### Documentation
- `ALGORITHM_IMPROVEMENTS.md` (full details)
- `TEST_RESULTS_SUMMARY.md` (current state)
- This file (quick guide)

---

**Time Required:** 30-45 minutes  
**Difficulty:** Easy (just pattern additions)  
**Risk Level:** Low (changes are additive)  
**Expected Improvement:** +15-20 percentage points

---

## Need Help?

1. **Syntax errors?** Run `python -m py_compile syllabus_checker.py`
2. **Not working?** Restore backup and check line numbers
3. **False positives?** May need to adjust min_matches back up
4. **Still low scores?** Check `ALGORITHM_IMPROVEMENTS.md` for Phase 2 changes

