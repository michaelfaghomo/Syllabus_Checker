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
    # Check if file was uploaded
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    
    # Check if file has a name
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({'error': 'File type not allowed. Please upload PDF, DOCX, or TXT files.'}), 400
    
    try:
        # Save the file temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Check the syllabus
        checker = SyllabusChecker()
        results = checker.check_syllabus(filepath)
        
        # Clean up the uploaded file
        os.remove(filepath)
        
        return jsonify(results)
    
    except Exception as e:
        return jsonify({'error': f'Error processing file: {str(e)}'}), 500

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
