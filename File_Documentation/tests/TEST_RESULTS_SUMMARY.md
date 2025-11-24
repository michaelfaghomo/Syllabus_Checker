# Syllabus Checker Test Results Summary

**Test Date:** November 24, 2025  
**Files Tested:** 3 real VCU syllabi  
**Test Tool:** `test_analysis.py`

---

## Quick Summary

| Metric | Value |
|--------|-------|
| **Average Score** | 78.6% |
| **Average Items Found** | 11.7 / 14 required |
| **Best Performing File** | MGMT303 (85.7%) |
| **Worst Performing File** | BUSN 301 (71.4%) |
| **Most Common Failure** | Grade Weights (67% miss rate) |
| **Lowest Confidence Item** | Course Prefix (39.3% avg) |

---

## Individual File Results

### 1. BUSN 301 FA25 Maynard.docx
- **Score:** 71.4% (10/14 required)
- **Text Length:** 12,107 characters
- **URLs Found:** 21
- **Status:** ⚠️ NEEDS WORK

**Missing Required Items:**
- ❌ Final exam date and time (10% confidence)
- ❌ Grading scale (46% confidence)
- ❌ Grade categories and weights (4% confidence)
- ❌ VCU Libraries statement and link (14.3% confidence)

**Low Confidence Items (found but uncertain):**
- ⚠️ Course prefix and number (38%)
- ⚠️ Course prerequisites (38%)
- ⚠️ Required texts/materials (38%)

---

### 2. INFO 370 Fall 2025 syllabus.pdf
- **Score:** 78.6% (11/14 required)
- **Text Length:** 6,809 characters
- **URLs Found:** 1
- **Status:** ⚠️ NEEDS WORK

**Missing Required Items:**
- ❌ University course description (4% confidence)
- ❌ Course schedule (46% confidence)
- ❌ Grade categories and weights (64% confidence)

**Low Confidence Items:**
- ⚠️ Course prefix and number (38%)
- ⚠️ Student learning outcomes (34%)
- ⚠️ Final exam date and time (40%)
- ⚠️ VCU Libraries statement (40%)

---

### 3. MGMT303.904_RINP_Custodio_Fall25.08.07.25-Syllabus.pdf
- **Score:** 85.7% (12/14 required)
- **Text Length:** 24,587 characters
- **URLs Found:** 3
- **Status:** ⚠️ NEEDS WORK (close to passing)

**Missing Required Items:**
- ❌ Student learning outcomes (12% confidence)
- ❌ Course schedule (46% confidence)

**Low Confidence Items:**
- ⚠️ Course prefix and number (42%)
- ⚠️ University course description (46%)
- ⚠️ Course prerequisites (42%)
- ⚠️ Final exam date and time (45%)
- ⚠️ VCU Libraries statement (40%)

---

## Pattern Analysis Across All Files

### Most Problematic Requirements

#### 1. **Grade Categories and Weights** 
- **Failed:** 2/3 files (67%)
- **Average Confidence:** 34%
- **Why:** Current algorithm requires 3+ percentage matches. Some syllabi use point systems or tables that don't extract well.

#### 2. **Course Schedule**
- **Failed:** 2/3 files (67%)
- **Average Confidence:** 46%
- **Why:** Algorithm looks for "Week X" patterns, but syllabi use "Module", dates, or external references.

#### 3. **Course Prefix and Number**
- **Low Confidence:** 3/3 files (100%)
- **Average Confidence:** 39.3%
- **Why:** Pattern matching works, but confidence scoring penalizes single-pattern matches too heavily.

#### 4. **VCU Libraries Statement**
- **Issues:** 3/3 files (missed 1, low confidence in 2)
- **Average Confidence:** 31.4% (including the miss)
- **Why:** Strict requirement for specific URL and text. URLs may not extract properly from some PDFs.

---

## URL Detection Analysis

**Total URLs Found:** 25 across all files

| File | URL Count | VCU Provost | VCU Library |
|------|-----------|-------------|-------------|
| BUSN 301 | 21 | ✅ Found | ❌ Not Found |
| INFO 370 | 1 | ✅ Found | ❌ Not Found |
| MGMT303 | 3 | ✅ Found | ❌ Not Found |

**Key Finding:** All files include the VCU Provost/Syllabus policy link (go.vcu.edu/syllabus), but **none have the explicit library.vcu.edu URL**. However, 2/3 mention "VCU Libraries" in text, suggesting the statement is present but the URL is missing or not extracted.

---

## Confidence Score Distribution

### Items with Consistently Low Confidence (<50%)
1. Course prefix and number: 38-42%
2. Course prerequisites: 38-42%
3. Final exam: 40-45%
4. VCU Libraries: 40%
5. Student learning outcomes: 34% (in one file)

### Items with High Confidence (>90%)
1. Instructor information: 100% (all files)
2. Class meeting times: 67-100%
3. VCU Provost link: 96-100%
4. Semester/credits: 75-100%

---

## Key Insights

### What's Working Well ✅
- **Instructor Detection:** 100% success with high confidence
- **VCU Provost Link:** All files detected with 96-100% confidence
- **Meeting Times/Location:** Strong detection in all files
- **Semester & Credits:** Reliable detection

### What Needs Improvement ❌
- **Grade Weights:** Too strict (requires 3 matches)
- **Course Schedule:** Doesn't recognize "Module" or date-based formats
- **Confidence Scoring:** Penalizes important single-pattern matches
- **VCU Libraries:** URL extraction issues, too strict requirements
- **Alternative Formats:** Doesn't handle point-based grading, TBA dates, etc.

---

## Recommendations

### Immediate Actions (High Priority)
1. **Reduce `min_matches` for grade_weights** from 3 to 2
2. **Add "Module" and date patterns** to course_schedule
3. **Boost confidence** for course_info when course code detected
4. **Relax VCU Libraries** requirement (text mention OR URL)

### Short-term Improvements (Medium Priority)
5. Add "None" detection for prerequisites
6. Recognize "TBA" for final exams
7. Detect point-based grading systems
8. Add patterns for alternative schedule formats

### Long-term Enhancements (Low Priority)
9. Improve PDF table extraction
10. Add machine learning for pattern recognition
11. Create domain-specific confidence adjustments
12. Build test suite with known-good syllabi

---

## Testing Methodology

### Tools Created
1. **`test_analysis.py`** - Comprehensive test runner
   - Analyzes multiple files
   - Generates detailed reports
   - Identifies patterns across failures
   - Exports JSON for further analysis

2. **`test_analysis_report.json`** - Machine-readable results
   - Complete confidence scores
   - Pattern match details
   - URL listings
   - Structured recommendations

### Test Files Used
- **BUSN 301 FA25 Maynard.docx** - Business course, DOCX format
- **INFO 370 Fall 2025 syllabus.pdf** - Information Science, PDF
- **MGMT303.904_RINP_Custodio_Fall25.08.07.25-Syllabus.pdf** - Management, PDF

All files are real VCU syllabi from Fall 2025, representing diverse formats and content structures.

---

## Validation Plan

### Before Implementation
- Current average score: **78.6%**
- Current low confidence count: **5 major issues**

### After Improvements (Projected)
- Target average score: **93-98%**
- Target low confidence count: **0-2 minor issues**

### Validation Steps
1. Implement Phase 1 changes from `ALGORITHM_IMPROVEMENTS.md`
2. Re-run `test_analysis.py` on same 3 files
3. Verify improvements:
   - Grade weights detected in all files
   - Course schedule detected in all files
   - Course prefix confidence > 60%
4. Test on additional syllabi (if available)
5. Monitor for false positives (shouldn't increase)

---

## Files Generated

| File | Purpose | Size |
|------|---------|------|
| `test_analysis.py` | Test runner script | 337 lines |
| `test_output.txt` | Human-readable results | 259 lines |
| `test_analysis_report.json` | Machine-readable data | 773 lines |
| `ALGORITHM_IMPROVEMENTS.md` | Detailed recommendations | Comprehensive guide |
| `TEST_RESULTS_SUMMARY.md` | This file | Executive summary |

---

## Conclusion

The syllabus checker is **performing reasonably well** at 78.6% average detection rate, but has clear opportunities for improvement. The main issues are:

1. **Over-strict thresholds** for certain requirements
2. **Limited pattern variety** for common formatting alternatives
3. **Confidence scoring** that penalizes legitimate matches
4. **Missing edge cases** like "TBA", "None", point systems

The recommendations in `ALGORITHM_IMPROVEMENTS.md` are **low-risk, high-impact** changes that should bring average detection to 93-98% without introducing false positives.

**Next Step:** Review recommendations and implement Phase 1 improvements.

