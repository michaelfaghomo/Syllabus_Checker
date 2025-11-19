// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const checkBtn = document.getElementById('checkBtn');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const removeBtn = document.getElementById('removeBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const newCheckBtn = document.getElementById('newCheckBtn');
const retryBtn = document.getElementById('retryBtn');
const uploadSection = document.querySelector('.upload-section');

let selectedFile = null;

// Event Listeners
browseBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
removeBtn.addEventListener('click', removeFile);
checkBtn.addEventListener('click', checkSyllabus);
newCheckBtn.addEventListener('click', resetForm);
retryBtn.addEventListener('click', resetForm);

// Drag and drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
});

uploadArea.addEventListener('click', (e) => {
    if (e.target === uploadArea || e.target.closest('.upload-icon') || e.target.closest('h2') || e.target.closest('p')) {
        fileInput.click();
    }
});

function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFile(file) {
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const maxSize = 16 * 1024 * 1024; // 16MB

    if (!allowedTypes.includes(file.type)) {
        alert('Please upload a PDF, DOCX, or TXT file.');
        return;
    }

    if (file.size > maxSize) {
        alert('File size must be less than 16MB.');
        return;
    }

    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.classList.remove('hidden');
    uploadArea.style.display = 'none';
    checkBtn.disabled = false;
}

function removeFile() {
    selectedFile = null;
    fileInput.value = '';
    fileInfo.classList.add('hidden');
    uploadArea.style.display = 'block';
    checkBtn.disabled = true;
}

async function checkSyllabus() {
    if (!selectedFile) return;

    // Hide sections
    uploadSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
        const response = await fetch('/api/check-syllabus', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        loadingSection.classList.add('hidden');

        if (data.error) {
            showError(data.error);
        } else {
            showResults(data);
        }
    } catch (error) {
        loadingSection.classList.add('hidden');
        showError('An error occurred while checking the syllabus. Please try again.');
    }
}

function showResults(data) {
    resultsSection.classList.remove('hidden');

    // Update summary
    const requiredScore = data.required.percentage;
    const requiredCount = `${data.required.found}/${data.required.total}`;
    
    document.getElementById('requiredScore').textContent = `${requiredScore}%`;
    document.getElementById('requiredCount').textContent = requiredCount;

    // Update summary status
    const summaryStatus = document.getElementById('summaryStatus');
    if (requiredScore >= 90) {
        summaryStatus.textContent = '🎉 Excellent! Your syllabus meets most requirements.';
    } else if (requiredScore >= 70) {
        summaryStatus.textContent = '👍 Good progress! Some items may need attention.';
    } else {
        summaryStatus.textContent = '⚠️ Several required items appear to be missing.';
    }

    // Display required items
    const requiredContainer = document.getElementById('requiredItems');
    requiredContainer.innerHTML = '';
    data.required.items.forEach(item => {
        requiredContainer.appendChild(createRequirementItem(item));
    });

    // Display recommended items
    const recommendedContainer = document.getElementById('recommendedItems');
    recommendedContainer.innerHTML = '';
    data.recommended.items.forEach(item => {
        recommendedContainer.appendChild(createRequirementItem(item));
    });
}

function createRequirementItem(item) {
    const div = document.createElement('div');
    div.className = `requirement-item ${item.found ? 'found' : 'not-found'}`;

    const icon = document.createElement('div');
    icon.className = 'requirement-icon';
    icon.textContent = item.found ? '✅' : '❌';

    const content = document.createElement('div');
    content.className = 'requirement-content';

    const name = document.createElement('div');
    name.className = 'requirement-name';
    name.textContent = item.name;

    const confidence = document.createElement('div');
    confidence.className = 'requirement-confidence';
    confidence.textContent = item.found 
        ? `Detected with ${item.confidence}% confidence`
        : `Not detected (${item.confidence}% confidence)`;

    content.appendChild(name);
    content.appendChild(confidence);
    div.appendChild(icon);
    div.appendChild(content);

    return div;
}

function showError(message) {
    errorSection.classList.remove('hidden');
    errorMessage.textContent = message;
}

function resetForm() {
    uploadSection.classList.remove('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    loadingSection.classList.add('hidden');
    removeFile();
}
