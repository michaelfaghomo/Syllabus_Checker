# VCU Syllabus Checker

A web application that allows VCU instructors to upload their syllabi and check them against the university's official syllabus requirements.

## Features

- 📄 **Multiple File Upload**: Upload and check multiple syllabi at once - supports PDF, DOCX, and TXT formats
- ✅ **Requirement Checking**: Validates against 14 required items and 2 recommended items
- 📊 **Batch Statistics**: View overall statistics when checking multiple files
- 📋 **Detailed Results**: Shows which requirements are met with confidence scores for each file
- 🎨 **Modern UI**: Clean, responsive design with VCU branding
- 🚀 **Fast Analysis**: Quick text extraction and pattern matching

## VCU Syllabus Requirements Checked

### Required Items (14)
1. Course prefix and number, section number, and title
2. Semester term and credit hours
3. Class meeting days/times/location (if applicable)
4. Instructor name, contact information, and office hours
5. University course description
6. Course prerequisites, if any
7. Student learning outcomes
8. Required texts and/or course materials
9. Course schedule
10. Final exam date and time (if applicable)
11. Grading scale
12. Grade categories and weights
13. Link to the VCU Syllabus Policy Statements on the Provost's Website
14. VCU Libraries statement and link (https://www.library.vcu.edu/)

### Recommended Items (2)
1. Department or course-specific attendance and punctuality policies
2. Department or course-specific technology and media policies

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
- **PyPDF2**: Extract text from PDF files
- **python-docx**: Extract text from DOCX files
- **Regular Expressions**: Pattern matching to detect required elements
- **Text Analysis**: Keyword detection and confidence scoring

The checker analyzes the uploaded document's text content and searches for patterns and keywords associated with each requirement. It provides a confidence score based on how many indicators are found for each item.

## Project Structure

```
workspace/
├── app.py                 # Flask application and API endpoints
├── syllabus_checker.py    # Core checking logic
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Main HTML page
├── static/
│   ├── css/
│   │   └── style.css     # Styling
│   └── js/
│       └── script.js     # Frontend JavaScript
└── uploads/              # Temporary file storage (auto-created)
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
    "items": [...]
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

## Notes

- This tool uses automated text analysis and may not catch all instances
- A manual review is still recommended to ensure complete compliance
- The confidence scores indicate the likelihood that a requirement is present
- Files are temporarily stored and immediately deleted after analysis

## License

This project is provided as-is for educational purposes.

## Support

For questions or issues, please contact your VCU IT support team or refer to the [VCU Provost Website](https://provost.vcu.edu/) for official syllabus guidelines.
