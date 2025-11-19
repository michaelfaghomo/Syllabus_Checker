# Changelog

## Version 2.0 - Multiple File Upload Support

### New Features
✨ **Batch Processing**: Upload and check multiple syllabi at once
- Select multiple files using the file picker
- Drag and drop multiple files simultaneously
- Individual file management (remove specific files before checking)
- File size display for each uploaded file

✨ **Batch Statistics**: Comprehensive overview when checking multiple files
- Total files processed
- Number of successful checks vs. errors
- Average score across all successful checks
- Average number of requirements found

✨ **Enhanced Results Display**:
- Individual result cards for each file
- Collapsible details for each file (Show/Hide Details button)
- File numbering for easy reference
- Mini summary cards showing quick stats for each file
- Error handling for individual files (one file error doesn't stop others)

### Improvements
- Updated UI text to reflect multiple file capability
- Better file list display with icons and sizes
- Improved loading messages for batch processing
- Mobile-responsive batch statistics grid
- Enhanced color coding and visual hierarchy

### Technical Changes
- Backend now accepts `files` (plural) parameter
- API returns array of results with batch statistics
- JavaScript refactored for multiple file handling
- New CSS classes for batch summary and result cards
- File validation applied per-file with error collection

## Version 1.0 - Initial Release

### Features
- Single file upload and analysis
- PDF, DOCX, and TXT support
- 14 required items checking
- 2 recommended items checking
- Confidence scoring
- Modern UI with VCU branding
- Text extraction and pattern matching
