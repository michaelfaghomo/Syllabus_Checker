# VCU Syllabus Checker

A web application that allows VCU instructors to upload their syllabi and check them against the university's official syllabus requirements.

## Features

- 📄 **Multiple File Upload**: Upload and check multiple syllabi at once - supports PDF, DOCX, and TXT formats
- ✅ **Requirement Checking**: Validates against 14 required items and 2 recommended items
- 🌐 **VCU Bulletin Integration**: Auto-validates course descriptions, prerequisites, and titles against official VCU Bulletin
- 🎯 **Granular Sub-Components**: First 4 requirements broken into sub-items with partial credit scoring
- 🔍 **Fuzzy Title Matching**: Detects close matches for course titles with similarity scoring

- 📊 **Batch Statistics**: View overall statistics when checking multiple files
- 📋 **Detailed Results**: Shows which requirements are met with confidence scores for each file
- 🎨 **Modern UI**: Clean, responsive design with VCU branding and collapsible details
- 🚀 **Fast Analysis**: Quick text extraction and pattern matching with 1-hour caching

## VCU Syllabus Requirements Checked

### Required Items (14)
1. **Course information** *(3 sub-items with partial credit)*
   - Course prefix and number (e.g., INFO 370)
   - Section number (e.g., 001, INFO370-003)
   - Course title (validated against VCU Bulletin with fuzzy matching)
2. **Semester and credit information** *(2 sub-items with partial credit)*
   - Semester term (Fall/Spring/Summer + year)
   - Credit hours
3. **Class meeting information** *(3 sub-items with partial credit)*
   - Meeting days (including online/asynchronous formats)
   - Meeting time
   - Meeting location (physical rooms or online/virtual/Zoom/Teams)
4. **Instructor information** *(3 sub-items with partial credit)*
   - Instructor name
   - Contact information (email/phone)
   - Office hours
5. **University course description** *(validated against VCU Bulletin)*
6. **Course prerequisites, if any** *(validated against VCU Bulletin, marked N/A if none)*
7. Student learning outcomes
8. Required texts and/or course materials
9. Course schedule
10. **Final exam date and time** *(or final project as replacement)*
11. **Grading scale** *(supports multiple formats: >=, >, "90 and above", decimals, points)*
12. Grade categories and weights
13. Link to the VCU Syllabus Policy Statements on the Provost's Website
14. VCU Libraries statement and link (https://www.library.vcu.edu/)

### Recommended Items (2)
1. Department or course-specific attendance and punctuality policies
2. Department or course-specific technology and media policies *(includes AI policy detection)*

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd workspace
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

**Dependencies include:**
- `Flask` - Web framework
- `PyPDF2` - PDF text extraction
- `python-docx` - DOCX text extraction
- `beautifulsoup4`, `requests`, `lxml` - VCU Bulletin web scraping
- `Flask-CORS`, `werkzeug` - Web server utilities

## Usage

1. Start the Flask application:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

3. Upload your syllabus file(s) - you can select multiple files at once!
   - PDF, DOCX, or TXT formats supported
   - Drag and drop multiple files or click to browse

4. Click "Check Syllabi" to analyze the documents

5. Review the results:
   - Batch summary showing overall statistics (for multiple files)
   - Individual results for each file with expandable details
   - Confidence scores for each requirement

## How It Works

The application uses:
- **Flask**: Web framework for the backend API
- **PyPDF2**: Extract text from PDF files (including URLs)
- **python-docx**: Extract text from DOCX files (including hyperlinks)
- **BeautifulSoup4 + Requests**: Web scraping for VCU Bulletin integration
- **Advanced Pattern Matching**: Multiple detection strategies per requirement
- **Context-Aware Analysis**: Finds sections even without clear headers
- **URL Extraction**: Identifies and validates VCU policy and library links
- **Weighted Scoring**: Confidence scores based on multiple indicators
- **In-Memory Caching**: 1-hour TTL for bulletin data to reduce API calls

### Enhanced Detection (v3.0)
The checker now uses **multi-strategy detection with external validation**:
1. **VCU Bulletin Integration**: Auto-detects course code and validates against official data
2. **URL Detection**: Extracts and validates all links
3. **Pattern Matching**: Flexible regex for various formats (including >=, <=, word-based operators)
4. **Context Analysis**: Understands content near keywords
5. **Text Patterns**: Detects requirements in paragraphs
6. **Required Phrases**: Ensures critical text is present
7. **Fuzzy Matching**: Detects close matches (70%+ similarity) with user notifications
8. **Partial Credit**: Sub-components allow granular scoring for complex requirements

This means the checker can find requirements even when:
- Sections lack clear headers
- Links are embedded differently
- Text uses non-standard phrasing
- Content is in paragraph form
- Course titles have minor variations
- Classes are online/virtual/remote
- Final projects replace traditional exams
- Prerequisites don't exist (marked N/A)

## Project Structure

```
workspace/
├── app.py                      # Flask application and API endpoints
├── syllabus_checker.py         # Core checking logic with sub-component support
├── vcu_bulletin_scraper.py     # VCU Bulletin web scraping and caching
├── debug_mode.py               # Detailed analysis tool for testing
├── test_analysis.py            # Batch testing utility
├── requirements.txt            # Python dependencies
├── templates/
│   └── index.html             # Main HTML page with collapsible UI
├── static/
│   ├── css/
│   │   └── style.css          # Styling with sub-item and special note styles
│   └── js/
│       └── script.js          # Frontend JavaScript with bulletin integration
├── test_samples/               # Sample syllabi for testing
└── uploads/                    # Temporary file storage (auto-created)
```

## API Endpoints

### `POST /api/check-syllabus`
Upload and check a syllabus file.

**Request**: multipart/form-data with file

**Response**:
```json
{
  "success": true,
  "required": {
    "total": 14,
    "found": 12,
    "percentage": 85.7,
    "items": [
      {
        "name": "Course information",
        "found": true,
        "confidence": 100,
        "has_sub_items": true,
        "sub_items": [
          {
            "name": "Course prefix and number",
            "found": true,
            "weight": 0.34
          },
          {
            "name": "Course title",
            "found": true,
            "weight": 0.33,
            "bulletin_check": {
              "official_text": "Data Communications and Networking",
              "exact_match": false,
              "similarity": 85
            },
            "special_note": "Note: Close match found (85% similar)..."
          }
        ]
      },
      {
        "name": "University course description",
        "found": true,
        "confidence": 100,
        "bulletin_check": {
          "official_text": "Official description...",
          "exact_match": true,
          "validation_method": "bulletin_exact_match"
        }
      },
      {
        "name": "Course prerequisites",
        "found": true,
        "confidence": 100,
        "isNotApplicable": true,
        "bulletin_check": {
          "official_text": "None",
          "validation_method": "not_applicable"
        }
      }
    ]
  },
  "recommended": {
    "total": 2,
    "found": 1,
    "items": [...]
  }
}
```

### `GET /api/requirements`
Get the list of all requirements.

## Testing & Debugging

### Upload Reference Files
```bash
# Place test syllabi in test_samples directory
cp ~/Downloads/my_syllabus.pdf test_samples/

# Run debug mode for detailed analysis
python3 debug_mode.py test_samples/my_syllabus.pdf
```

### Debug Mode Features
- Detailed match information for each requirement and sub-item
- **VCU Bulletin validation results** (course code, description, prerequisites, title)
- List of all URLs found in document
- Specific recommendations for improvement
- Confidence score breakdowns with partial credit calculations
- Text extraction preview
- **Special notes** for fuzzy matches and final project detection

See `test_samples/README.md` for test results and `File_Documentation/` for complete technical documentation.

## VCU Bulletin Integration (v3.0)

The checker now **automatically validates** course information against the official VCU Bulletin:

### Auto-Detection
- Extracts course code (e.g., "INFO 370") from syllabus
- Fetches official data from VCU Bulletin website
- No manual input required!

### Validation Features
**Course Description:**
- ✅ Exact match: Word-for-word presence (case-insensitive)
- ⚠️ Warns if description doesn't match official text
- Shows official description for reference

**Prerequisites:**
- ✅ Flexible course code matching (e.g., "INFO 161" or "INFO161")
- ℹ️ Marked as "N/A" if course has no prerequisites
- Shows which prerequisite courses were found/missing

**Course Title:**
- ✅ Exact match validation
- ⚠️ Fuzzy matching (70%+ similarity) with user notification
- Handles word reordering and abbreviations

### Caching & Performance
- **In-memory cache**: 1-hour TTL to reduce requests
- **Graceful degradation**: System works even if bulletin unavailable
- **Error handling**: Network timeouts, parsing failures handled safely

## Algorithm Improvements (v3.0)

**Major enhancements:**
- 🌐 **VCU Bulletin Integration**: Auto-validates course info against official data
- 🎯 **Granular Sub-Components**: Partial credit for complex requirements
- 🔍 **Fuzzy Title Matching**: Detects close matches with similarity scoring
- ✅ **Enhanced Grade Scales**: Supports >=, <=, word operators ("90 and above")
- 📝 **Final Project Detection**: Special notes when projects replace exams
- ℹ️ **N/A Prerequisites**: Proper handling of courses without prerequisites
- 🎨 **Collapsible UI**: Better organization with expandable detail sections
- ✅ **Better URL Detection**: Finds VCU policy and library links more reliably
- ✅ **Context-Aware**: Detects sections without clear headers
- ✅ **Multi-Strategy**: Uses multiple detection methods per requirement

See `File_Documentation/` for detailed technical information and improvement summaries.

## Notes

- This tool uses advanced text analysis and VCU Bulletin validation, but manual review is still recommended
- Confidence scores indicate likelihood (>80% = very likely present)
- **Sub-components** allow partial credit (e.g., 67% if 2 of 3 items found)
- **Special notes** alert you to detected variations (fuzzy title match, final project instead of exam)
- Files are temporarily stored and immediately deleted after analysis
- Use `debug_mode.py` to understand why something was or wasn't detected
- The algorithm works best with clear section headers but can find content without them
- **VCU Bulletin integration** requires internet connection; falls back to pattern matching if unavailable
- **Prerequisites marked N/A** when officially none exist (not counted as missing)

## License

This project is provided as-is for educational purposes.

## Support

For questions or issues, please contact your VCU IT support team or refer to the [VCU Provost Website](https://provost.vcu.edu/) for official syllabus guidelines.
