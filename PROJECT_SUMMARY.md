# VCU Syllabus Checker - Complete Project Summary

## 🎯 Project Overview

A web application that allows VCU instructors to upload and check syllabi against the university's official requirements. **Now supports checking multiple syllabi at once!**

## 📦 What's Included

### Core Application Files
- **`app.py`** (~127 lines) - Flask backend with multiple file upload API
- **`syllabus_checker.py`** (~1,085 lines) - Core checking logic with sub-components, VCU Bulletin validation, fuzzy matching
- **`vcu_bulletin_scraper.py`** (~200 lines) - Web scraping module with caching for VCU Bulletin integration
- **`templates/index.html`** (~124 lines) - Main web interface
- **`static/js/script.js`** (~547 lines) - Frontend logic with bulletin display, collapsible details, sub-items
- **`static/css/style.css`** (~875 lines) - Complete styling with VCU branding, sub-item styles, special notes

### Configuration & Dependencies
- **`requirements.txt`** - Python dependencies (Flask, PyPDF2, python-docx, beautifulsoup4, requests, lxml)
- **`run.sh`** - Quick startup script
- **`.gitignore`** - Exclude temporary files and uploads

### Testing & Debug Tools
- **`debug_mode.py`** - Detailed analysis tool with VCU Bulletin validation results
- **`test_samples/`** - Sample syllabi with documented test results

### Documentation
- **`README.md`** - Complete project documentation
- **`QUICKSTART.md`** - Quick start guide for users
- **`CHANGELOG.md`** - Version history and changes
- **`MULTIPLE_FILES_FEATURE.md`** - Detailed feature documentation
- **`PROJECT_SUMMARY.md`** - This file

**Total:** ~2,960 lines of code across 6 main files

## ✨ Key Features

### Version 3.0 - VCU Bulletin Integration & Enhanced Validation
1. **VCU Bulletin Auto-Validation** 🌐
   - Auto-detects course code from syllabus
   - Validates course description against official VCU Bulletin
   - Validates prerequisites with flexible matching
   - Validates course title with fuzzy matching (70%+ similarity)
   - Marks prerequisites as N/A when none exist
   - 1-hour in-memory caching for performance
   - Graceful degradation if bulletin unavailable

2. **Granular Sub-Components** 🎯
   - First 4 requirements broken into 11 sub-items
   - Partial credit scoring (e.g., 0.67/1.00 for 2 of 3 items)
   - Course info: prefix/number, section, title
   - Semester info: term, credit hours
   - Meeting info: days, time, location (online support)
   - Instructor info: name, contact, office hours

3. **Enhanced Pattern Detection** 🔍
   - **Fuzzy Title Matching**: Detects close matches with similarity scoring
   - **Grade Scales**: Supports >=, <=, "90 and above", decimals, points
   - **Final Projects**: Detects when projects replace exams with special notes

4. **User Experience Improvements** 🎨
   - Collapsible detail sections for cleaner UI
   - Special warning notes for fuzzy matches and variations
   - Sub-item checkmarks showing granular progress
   - Official VCU text display for validation
   - N/A indicators for non-applicable requirements

### Version 2.0 - Multiple File Support
1. **Batch Processing**
   - Upload multiple syllabi simultaneously
   - Drag and drop multiple files
   - Individual file management
   - File size display

2. **Batch Statistics**
   - Total files processed
   - Success/failure counts
   - Average compliance score
   - Average items found

3. **Individual Results**
   - Separate card for each file
   - Expandable details view
   - File numbering
   - Error handling per file

### Core Features (All Versions)
1. **Requirements Checking**
   - 14 required VCU items (with 11 sub-components)
   - 2 recommended items
   - Multi-strategy confidence scoring (0-100%)

2. **File Format Support**
   - PDF files
   - DOCX files
   - TXT files
   - Max 16MB per file

3. **Modern UI**
   - VCU gold/black branding
   - Responsive design
   - Smooth animations
   - Mobile-friendly

## 📋 VCU Requirements Checked

### Required (14 items with 11 sub-components)
1. **Course information** *(3 sub-items)*
   - ✓ Course prefix and number
   - ✓ Section number (supports INFO300-003 format)
   - ✓ Course title (validated against VCU Bulletin)
2. **Semester and credit information** *(2 sub-items)*
   - ✓ Semester term (Fall/Spring/Summer + year)
   - ✓ Credit hours
3. **Class meeting information** *(3 sub-items)*
   - ✓ Meeting days
   - ✓ Meeting time
   - ✓ Meeting location (physical or online/Zoom/Teams/remote)
4. **Instructor information** *(3 sub-items)*
   - ✓ Instructor name
   - ✓ Contact information
   - ✓ Office hours
5. **University course description** *(validated against VCU Bulletin)*
6. **Course prerequisites** *(validated against VCU Bulletin, marked N/A if none)*
7. Student learning outcomes
8. Required texts and materials
9. Course schedule
10. **Final exam date and time** *(or final project as replacement)*
11. **Grading scale** *(supports >=, <=, "90 and above", decimals, points)*
12. Grade categories and weights
13. VCU Syllabus Policy link
14. VCU Libraries statement and link

### Recommended (2 items)
1. Attendance and punctuality policies
2. **Technology and media policies** *(includes AI policy detection)*

## 🚀 Quick Start

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
./run.sh
# OR
python3 app.py
```

### Usage
1. Open browser to `http://localhost:5000`
2. Upload one or more syllabus files
3. Click "Check Syllabi"
4. Review results and batch statistics

## 🎨 User Interface

### Upload Section
- Drag-and-drop zone
- File browser button
- File list with sizes
- Remove individual files

### Results Section (Multiple Files)
```
┌─────────────────────────────────────┐
│   📊 Batch Summary                  │
│   ├── Total Files: 5                │
│   ├── Successful: 5                 │
│   ├── Avg Score: 85.7%              │
│   └── Avg Found: 12/14              │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ #1 BIOL3001_syllabus.pdf            │
│ ├── Score: 100% | Found: 14/14     │
│ └── [Show Details] ▼               │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ #2 CHEM2001_syllabus.docx           │
│ ├── Score: 85.7% | Found: 12/14    │
│ └── [Show Details] ▼               │
└─────────────────────────────────────┘
```

## 🔧 Technical Architecture

### Backend (Flask)
```
/api/check-syllabus [POST]
├── Accept: multipart/form-data (files)
├── Process: 
│   ├── Extract text from PDF/DOCX/TXT
│   ├── Auto-detect course code
│   ├── Fetch VCU Bulletin data (with caching)
│   ├── Pattern matching with sub-components
│   ├── Bulletin validation (description, prereqs, title)
│   └── Fuzzy matching and special notes
└── Return: Batch stats + individual results + bulletin data

/api/requirements [GET]
└── Return: List of all requirements
```

### VCU Bulletin Scraper Module
```python
BulletinCache (in-memory, 1-hour TTL)
├── parse_course_code(text) → (prefix, number)
├── build_bulletin_url(prefix, number) → URL
├── scrape_course_data(prefix, number) → dict
│   ├── Extract course paragraph
│   ├── Parse title, description, prerequisites, credits
│   └── Handle errors (timeout, network, parsing)
└── Cache management (get, set, cleanup)
```

### Frontend (Vanilla JS)
- File selection and validation
- FormData API for uploads
- Dynamic result rendering with sub-items
- Bulletin validation display
- Collapsible detail sections
- Special note alerts
- Toggle expand/collapse

### Text Analysis (Multi-Strategy)
1. URL detection and validation
2. Primary pattern matching (regex)
3. Text pattern matching
4. Required phrase checking
5. Context keyword analysis
6. Minimum text length validation
7. Fuzzy matching (word-based similarity)
8. VCU Bulletin validation

### Confidence Scoring Algorithm
```
Normal Path:
├── pattern_score = matches × 30
├── context_score = (context_matches / total_keywords) × 20
├── url_bonus = 20 (if URL found)
└── confidence = min(100, pattern_score + context_score + url_bonus)

Penalty Path (missing required phrases):
└── confidence = min(40, calculated_percentage)

Decision: found = (matches ≥ min_matches) AND (confidence ≥ 25%)
```

## 📊 Project Statistics

- **Total Lines of Code**: ~2,960
- **Core Files**: 6 main application files
- **Languages**: Python, JavaScript, HTML, CSS
- **Dependencies**: 8 Python packages (Flask, PyPDF2, python-docx, beautifulsoup4, requests, lxml, werkzeug, Flask-CORS)
- **File Formats**: 3 (PDF, DOCX, TXT)
- **Requirements Checked**: 16 (14 required with 11 sub-components + 2 recommended)
- **Sub-Components**: 11 granular items with partial credit
- **Confidence Threshold**: 25% minimum
- **Caching**: 1-hour TTL for VCU Bulletin data
- **Detection Strategies**: 8 multi-strategy methods per requirement

## 🎯 Use Cases

1. **Individual Instructor**: Check your syllabi before semester starts
2. **Department Head**: Review all department syllabi in one batch
3. **Quality Assurance**: Verify compliance across multiple courses
4. **New Faculty**: Ensure syllabi meet VCU standards
5. **Syllabus Update**: Quick check after revisions

## ⚡ Performance

- **Single File (cached)**: ~1-2 seconds
- **Single File (first request)**: ~2-4 seconds (includes VCU Bulletin scraping)
- **Multiple Files (5)**: ~5-15 seconds (depending on cache hits)
- **Max File Size**: 16MB per file
- **Concurrent Processing**: Sequential (safe file handling)
- **Caching**: 1-hour TTL reduces repeated requests to VCU Bulletin
- **Cache Hit**: <10ms for bulletin data
- **Cache Miss**: ~1-2 seconds for bulletin scraping

## 🔒 Security & Privacy

- ✅ Files stored temporarily only
- ✅ Automatic deletion after analysis
- ✅ No data retention
- ✅ Secure filename handling
- ✅ File type validation
- ✅ Size limit enforcement

## 🎓 VCU Branding

- Primary Color: Gold (#F8B229)
- Secondary Color: Black (#000000)
- Success: Green (#22c55e)
- Warning: Orange (#f59e0b)
- Danger: Red (#ef4444)

## 📱 Browser Compatibility

- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers
- ✅ Responsive design

## ✅ Recently Implemented (v3.0)

### VCU Bulletin Integration
- ✅ Auto-detect course code from syllabus
- ✅ Validate course description against official bulletin
- ✅ Validate prerequisites with flexible matching
- ✅ Validate course title with fuzzy matching
- ✅ In-memory caching with 1-hour TTL
- ✅ Graceful degradation and error handling

### Enhanced Detection
- ✅ Granular sub-components with partial credit
- ✅ Fuzzy title matching (70%+ similarity)
- ✅ Enhanced grade scale patterns (>=, word operators)
- ✅ Final project detection with special notes
- ✅ N/A prerequisites handling
- ✅ AI policy detection
- ✅ Collapsible UI sections

## 🚧 Future Enhancements (Potential)

### Performance & Caching
- [ ] **Stale-While-Revalidate (SWR) Caching**: Implement SWR strategy for VCU Bulletin data
  - Return cached data immediately (even if expired) for instant response
  - Refresh stale cache in background thread for next request
  - Improves user experience: <10ms response vs 2 second scrape
  - Course data changes rarely (once per semester) - ideal use case for SWR
  - Maintains data accuracy while maximizing speed
- [ ] **Persistent Cache**: Redis or database for cache across server restarts

### Export & Integration
- [ ] Export results to PDF/CSV
- [ ] Save/load previous checks
- [ ] Email results to instructor
- [ ] Integration with Canvas LMS

### File Format Support
- [ ] **Google Docs Integration**: Direct URL-based syllabus checking
  - **Overview**: Allow users to submit Google Docs URLs instead of uploading files
  - **Architecture**: Frontend URL input → Backend Google Docs API → Text extraction → Existing checker pipeline
  - **Dependencies**: `google-api-python-client`, `google-auth-httplib2`, `google-auth-oauthlib`, Google Cloud Project with OAuth 2.0
  - **Key Components**: OAuth authentication flow, Google Docs API client, permission validation, rate limiting
  - **User Flow**: User shares Doc → Pastes URL → System requests read access → Extracts text → Returns results
  - **Challenges**: OAuth setup, handling permissions, rate limits, maintaining user privacy
- [ ] HTML/Markdown support (.html, .md files)
- [ ] RTF/ODT support for legacy formats

### Advanced Features
- [ ] AI-powered suggestions
- [ ] Comparison between syllabi
- [ ] Template generation
- [ ] Multi-language support

## 📄 License & Usage

This project is created for VCU faculty and staff. Always manually review syllabi to ensure complete compliance with VCU policies.

## 🤝 Support

For questions about:
- **VCU Syllabus Requirements**: Visit [VCU Provost Website](https://provost.vcu.edu/)
- **Technical Issues**: Check documentation or contact IT support
- **Feature Requests**: Submit feedback through appropriate channels

## 🎉 Success Metrics

A well-formed syllabus should score:
- ✅ **90-100%**: Excellent - All requirements met
- ⚠️ **70-89%**: Good - Minor items may be missing
- ❌ **Below 70%**: Needs work - Several items missing

---

**Version**: 3.0  
**Last Updated**: January 27, 2026  
**Status**: ✅ Production Ready  
**Multiple File Support**: ✅ Enabled  
**VCU Bulletin Integration**: ✅ Active  
**Sub-Component Checking**: ✅ Active  
**Fuzzy Matching**: ✅ Enabled  
**Online Class Support**: ✅ Comprehensive

## 🏁 Ready to Use!

The application is fully functional with advanced VCU Bulletin validation, granular sub-component checking, and comprehensive online class support. Simply run `./run.sh` and start checking syllabi with confidence!
