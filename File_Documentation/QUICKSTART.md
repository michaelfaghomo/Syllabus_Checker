# Quick Start Guide

## Starting the Application

### Option 1: Using the startup script
```bash
./run.sh
```

### Option 2: Direct Python command
```bash
python3 app.py
```

The application will start on `http://localhost:5000`

## Using the Application

1. **Open your browser** and navigate to `http://localhost:5000`

2. **Upload syllabus files**:
   - Click "Browse Files" or drag and drop your files
   - **NEW**: Select multiple files at once! 
   - Supported formats: PDF, DOCX, TXT
   - Maximum file size: 16MB per file
   - You can remove individual files before checking

3. **Check the syllabi**:
   - Click "Check Syllabi" button
   - Wait for the analysis to complete (usually takes 1-3 seconds per file)

4. **Review results**:
   - **Batch Summary** (for multiple files): See overall statistics across all files
     - Total files processed
     - Number of successful checks
     - Average score and items found
   - **Individual Results**: Each file has its own card showing:
     - Overall score and requirements met
     - Expandable details with all required/recommended items
     - Confidence scores for each requirement
     - Green checkmarks (✅) indicate found items
     - Red X marks (❌) indicate missing items

5. **Check more syllabi**:
   - Click "Check More Syllabi" to start over

## What Gets Checked

### Required Items (14)
- ✅ Course prefix and number, section number, and title
- ✅ Semester term and credit hours
- ✅ Class meeting days/times/location
- ✅ Instructor name, contact information, and office hours
- ✅ University course description
- ✅ Course prerequisites
- ✅ Student learning outcomes
- ✅ Required texts and/or course materials
- ✅ Course schedule
- ✅ Final exam date and time
- ✅ Grading scale
- ✅ Grade categories and weights
- ✅ Link to VCU Syllabus Policy Statements
- ✅ VCU Libraries statement and link

### Recommended Items (2)
- 💡 Attendance and punctuality policies
- 💡 Technology and media policies

## Understanding Confidence Scores

The confidence score indicates how strongly the system detected each requirement:
- **70-100%**: Very likely present
- **40-69%**: Likely present, may need verification
- **Below 40%**: May be missing or not clearly stated

## Tips for Best Results

1. **Batch checking**: Upload multiple syllabi at once to quickly check all your courses
2. **Use clear headers** in your syllabus (e.g., "Course Description", "Grading Scale")
3. **Include complete information** for each required item
4. **Use the exact VCU Libraries link**: https://www.library.vcu.edu/
5. **Include the Provost website link** for syllabus policies
6. **Format consistently** throughout the document

## Troubleshooting

**"Unable to extract text from file"**
- Ensure the PDF is not scanned/image-only
- Try converting to DOCX or TXT format

**Low confidence scores for items you know are present**
- The system uses keyword detection - try using more standard terminology
- Ensure items are clearly labeled with headers

**File upload fails**
- Check file size is under 16MB
- Verify file format is PDF, DOCX, or TXT

## Important Notes

⚠️ **This is an automated tool** - it uses pattern matching and keyword detection. Always manually review your syllabus to ensure it meets all VCU requirements completely and accurately.

⚠️ **Privacy**: Uploaded files are temporarily stored during analysis and immediately deleted afterward. No data is retained.

## Need Help?

For official VCU syllabus requirements, visit:
- [VCU Provost Website](https://provost.vcu.edu/)
- [VCU Syllabus Policy Statements](https://provost.vcu.edu/)

---

**Version 1.0** | Built for VCU Faculty
