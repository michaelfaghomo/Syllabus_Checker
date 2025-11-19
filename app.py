from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import re
from syllabus_checker import SyllabusChecker

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/check-syllabus', methods=['POST'])
def check_syllabus():
    # Check if files were uploaded
    if 'files' not in request.files:
        return jsonify({'error': 'No files uploaded'}), 400
    
    files = request.files.getlist('files')
    
    # Check if any files were selected
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No files selected'}), 400
    
    results_list = []
    checker = SyllabusChecker()
    
    for file in files:
        # Skip empty filenames
        if file.filename == '':
            continue
            
        # Check if file type is allowed
        if not allowed_file(file.filename):
            results_list.append({
                'filename': file.filename,
                'error': 'File type not allowed. Please upload PDF, DOCX, or TXT files.'
            })
            continue
        
        try:
            # Save the file temporarily
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Check the syllabus
            results = checker.check_syllabus(filepath)
            results['filename'] = file.filename
            
            # Clean up the uploaded file
            os.remove(filepath)
            
            results_list.append(results)
        
        except Exception as e:
            results_list.append({
                'filename': file.filename,
                'error': f'Error processing file: {str(e)}'
            })
    
    # Calculate batch statistics
    successful_checks = [r for r in results_list if 'error' not in r]
    failed_checks = [r for r in results_list if 'error' in r]
    
    batch_stats = {
        'total_files': len(results_list),
        'successful': len(successful_checks),
        'failed': len(failed_checks)
    }
    
    if successful_checks:
        avg_required_percentage = sum(r['required']['percentage'] for r in successful_checks) / len(successful_checks)
        avg_required_found = sum(r['required']['found'] for r in successful_checks) / len(successful_checks)
        batch_stats['average_required_percentage'] = round(avg_required_percentage, 1)
        batch_stats['average_required_found'] = round(avg_required_found, 1)
    
    return jsonify({
        'success': True,
        'batch_stats': batch_stats,
        'results': results_list
    })

@app.route('/api/requirements', methods=['GET'])
def get_requirements():
    """Return the list of requirements"""
    return jsonify({
        'required': [
            'Course prefix and number, section number, and title',
            'Semester term and credit hours',
            'Class meeting days/times/location (if applicable)',
            'Instructor name, contact information, and office hours',
            'University course description (required to be verbatim from the University Bulletin)',
            'Course prerequisites, if any',
            'Student learning outcomes',
            'Required texts and/or course materials',
            'Course schedule',
            'Final exam date and time (if applicable)',
            'Grading scale',
            'Grade categories and weights',
            'Link to the VCU Syllabus Policy Statements on the Provost\'s Website',
            'The following statement and link: Use VCU Libraries to find and access library resources, spaces, technology and services that support and enhance all learning opportunities at the university. (https://www.library.vcu.edu/)'
        ],
        'recommended': [
            'Department or course-specific attendance and punctuality policies, if any',
            'Department or course-specific technology and media policies (e.g., recording class, expected email response time, etc.), if any'
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
