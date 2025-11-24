# Testing Guide - How to Upload and Test Syllabi

## 🎯 Overview

This guide explains how to upload reference PDF documents for testing and improving the syllabus checker algorithm.

## 📤 Method 1: Upload Via Web Interface

### Steps:
1. **Start the application:**
   ```bash
   ./run.sh
   ```

2. **Open your browser** to `http://localhost:5000`

3. **Upload your syllabus files:**
   - Click "Browse Files" or drag-and-drop
   - Select one or multiple PDF/DOCX/TXT files
   - Click "Check Syllabi"

4. **Review Results:**
   - See overall compliance score
   - Check which requirements were found
   - Review confidence levels for each item

### What to Look For:
- ❌ **False Negatives**: Items that ARE in your syllabus but weren't detected
- ⚠️ **Low Confidence**: Items detected with <60% confidence (may need clearer headers)
- ✅ **High Confidence**: Items detected with >80% confidence (well-formatted)

## 🔍 Method 2: Debug Mode (Detailed Analysis)

For **detailed debugging information** about what the checker is finding (or missing):

### Steps:
1. **Place your test file** in the `test_samples/` directory:
   ```bash
   cp ~/Downloads/my_syllabus.pdf test_samples/
   ```

2. **Run debug mode:**
   ```bash
   python3 debug_mode.py test_samples/my_syllabus.pdf
   ```

3. **Review detailed output:**
   - Extracted text preview
   - All URLs found
   - Detailed match information for each requirement
   - Specific recommendations for improvement

### Example Output:
```
============================================================
 VCU SYLLABUS CHECKER - DEBUG MODE
============================================================

📄 File: test_samples/biology_syllabus.pdf
📊 Size: 125,430 bytes

------------------------------------------------------------
 Extracting Text
------------------------------------------------------------
✅ Successfully extracted 4,523 characters
📝 First 200 characters:
   BIOL 3001 - Molecular Biology Fall 2024 3 Credit Hours...

------------------------------------------------------------
 Extracting URLs
------------------------------------------------------------
🔗 Found 3 URLs:
   1. https://provost.vcu.edu/faculty/handbook/syllabus
   2. https://www.library.vcu.edu/
   3. https://canvas.vcu.edu

------------------------------------------------------------
 Checking Requirements
------------------------------------------------------------

✅ Course prefix and number, section number, and title
   Confidence: [████████████████████] 95.0%
   Matches found:
      • Pattern match: \b[A-Z]{2,4}\s*-?\s*\d{3,4}
      • Found URL: BIOL 3001

❌ Link to VCU Syllabus Policy Statements
   Confidence: [████░░░░░░░░░░░░░░░░] 35.0%
   ⚠️  Not detected - consider adding clearer labels
```

### Save Results:
```bash
python3 debug_mode.py test_samples/my_syllabus.pdf > debug_results.txt
```

## 📁 Method 3: Store Reference Files Locally

### Create Test Samples Directory:
```bash
mkdir -p test_samples
cd test_samples
```

### Add Your Files:
```bash
# Copy from downloads
cp ~/Downloads/*.pdf .

# Or create a samples subdirectory
mkdir samples_spring_2024
cp ~/Documents/syllabi/*.pdf samples_spring_2024/
```

### Directory Structure:
```
test_samples/
├── README.md
├── biology_101_syllabus.pdf
├── chemistry_201_syllabus.pdf
├── english_301_syllabus.docx
└── samples_spring_2024/
    ├── course1.pdf
    ├── course2.pdf
    └── course3.pdf
```

## 🔬 What Makes a Good Test Sample?

Include syllabi that:
1. ✅ **Have all required components** (for baseline testing)
2. ⚠️ **Are missing some components** (to test detection)
3. 📝 **Use different formatting styles** (headers, no headers, etc.)
4. 🔗 **Have links in different formats** (hyperlinks, plain text URLs)
5. 📍 **Use various VCU locations** (different buildings, online, hybrid)
6. 📚 **State prerequisites differently** ("None", "Prereq: X", "Must have completed")

## 🐛 Reporting Issues

If the checker misses something that's clearly in your syllabus:

### Step 1: Run Debug Mode
```bash
python3 debug_mode.py your_syllabus.pdf > issue_report.txt
```

### Step 2: Note What Was Missed
Document:
- Which requirement was missed
- Exact text from your syllabus
- Page number or section
- Any unusual formatting

### Step 3: Share Findings
The debug output will help improve the detection algorithm. Look for patterns in what's being missed.

## 🎓 Common Issues and Solutions

### Issue: "Link to VCU Syllabus Policy" not detected

**Solutions:**
1. Make sure the URL is visible: `https://provost.vcu.edu/`
2. Include text like: "VCU Syllabus Policy Statements"
3. Reference: "See Provost's website for syllabus policies"

### Issue: "VCU Libraries statement" not detected

**Required elements:**
1. Must mention "VCU Libraries"
2. Must include URL: `https://www.library.vcu.edu/`
3. Recommended text: "Use VCU Libraries to find and access library resources..."

### Issue: Low confidence scores

**Causes:**
- Section without clear header
- Embedded in paragraph text
- Unusual formatting or spacing

**Solutions:**
- Add clear section headers (e.g., "Course Prerequisites:")
- Use standard terminology
- Separate sections with whitespace

### Issue: False positives

**Causes:**
- Similar keywords in different context
- URLs from external sources

**Solutions:**
- Use more specific headers
- Clearly label each section

## 📊 Batch Testing

Test multiple files at once via web interface:

1. **Select all test files** (hold Ctrl/Cmd)
2. **Upload batch**
3. **Review batch statistics:**
   - Which files scored highest
   - Common missing items across files
   - Average compliance rate

This helps identify patterns across your department's syllabi.

## 🔒 Privacy & Security

### Best Practices:
- ✅ Use **anonymized** syllabi for testing
- ✅ Remove student names/emails
- ✅ Use template versions
- ❌ Don't commit actual student data to git
- ❌ Don't include sensitive information

### Files are NOT stored:
- Uploaded files are **deleted immediately** after analysis
- No data is retained on the server
- Use for testing safely

## 💡 Pro Tips

1. **Test Before Semester**: Run all your syllabi through the checker before classes start
2. **Compare Years**: See how your syllabi improve over time
3. **Department Review**: Batch check all department syllabi for consistency
4. **Template Creation**: Use high-scoring syllabi as templates
5. **Debug Mode First**: When something's wrong, run debug mode to see exactly what's happening

## 🆘 Need Help?

1. Check the debug output first
2. Review the detailed match information
3. Compare with a high-scoring syllabus
4. Look at the sample URLs found
5. Check that required text is present

---

**Remember:** The checker is a tool to help ensure compliance, but manual review is still important!
