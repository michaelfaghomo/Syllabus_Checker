// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const checkBtn = document.getElementById('checkBtn');
const fileList = document.getElementById('fileList');
const addMoreBtn = document.getElementById('addMoreBtn');
const addMoreInput = document.getElementById('addMoreInput');
const loadingSection = document.getElementById('loadingSection');
const loadingMessage = document.getElementById('loadingMessage');
const progressMessage = document.getElementById('progressMessage');
const resultsSection = document.getElementById('resultsSection');
const errorSection = document.getElementById('errorSection');
const errorMessage = document.getElementById('errorMessage');
const newCheckBtn = document.getElementById('newCheckBtn');
const retryBtn = document.getElementById('retryBtn');
const uploadSection = document.querySelector('.upload-section');

let selectedFiles = [];

// Event Listeners
browseBtn.addEventListener('click', () => fileInput.click());
fileInput.addEventListener('change', handleFileSelect);
addMoreBtn.addEventListener('click', () => addMoreInput.click());
addMoreInput.addEventListener('change', handleAddMoreFiles);
checkBtn.addEventListener('click', checkSyllabi);
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
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
        handleFiles(files);
    }
});

uploadArea.addEventListener('click', (e) => {
    if (e.target === uploadArea || e.target.closest('.upload-icon') || e.target.closest('h2') || e.target.closest('p')) {
        fileInput.click();
    }
});

function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
        handleFiles(files);
    }
}

function handleFiles(files) {
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    const validFiles = [];
    const errors = [];
    
    files.forEach(file => {
        if (!allowedTypes.includes(file.type)) {
            errors.push(`${file.name}: Invalid file type`);
        } else if (file.size > maxSize) {
            errors.push(`${file.name}: File too large (max 16MB)`);
        } else {
            validFiles.push(file);
        }
    });
    
    if (errors.length > 0) {
        alert('Some files were skipped:\n' + errors.join('\n'));
    }
    
    if (validFiles.length > 0) {
        selectedFiles = validFiles;
        displayFileList();
        uploadArea.style.display = 'none';
        addMoreBtn.style.display = 'inline-block';
        checkBtn.disabled = false;
    }
}

function handleAddMoreFiles(e) {
    const files = Array.from(e.target.files);
    if (files.length > 0) {
        appendFiles(files);
    }
    // Clear the input so the same files can be selected again if needed
    e.target.value = '';
}

function appendFiles(files) {
    const allowedTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    const maxSize = 16 * 1024 * 1024; // 16MB
    
    const validFiles = [];
    const errors = [];
    const duplicates = [];
    
    files.forEach(file => {
        // Check if file already exists
        const isDuplicate = selectedFiles.some(existingFile => 
            existingFile.name === file.name && existingFile.size === file.size
        );
        
        if (isDuplicate) {
            duplicates.push(file.name);
        } else if (!allowedTypes.includes(file.type)) {
            errors.push(`${file.name}: Invalid file type`);
        } else if (file.size > maxSize) {
            errors.push(`${file.name}: File too large (max 16MB)`);
        } else {
            validFiles.push(file);
        }
    });
    
    if (errors.length > 0) {
        alert('Some files were skipped:\n' + errors.join('\n'));
    }
    
    if (duplicates.length > 0) {
        alert('Duplicate files skipped:\n' + duplicates.join('\n'));
    }
    
    if (validFiles.length > 0) {
        selectedFiles = selectedFiles.concat(validFiles);
        displayFileList();
    }
}

function displayFileList() {
    fileList.innerHTML = '';
    fileList.classList.remove('hidden');
    
    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';
        
        const fileIcon = document.createElement('span');
        fileIcon.className = 'file-icon';
        fileIcon.textContent = '📄';
        
        const fileName = document.createElement('span');
        fileName.className = 'file-name';
        fileName.textContent = file.name;
        
        const fileSize = document.createElement('span');
        fileSize.className = 'file-size';
        fileSize.textContent = formatFileSize(file.size);
        
        const removeBtn = document.createElement('button');
        removeBtn.className = 'file-remove-btn';
        removeBtn.textContent = '✕';
        removeBtn.onclick = () => removeFile(index);
        
        fileItem.appendChild(fileIcon);
        fileItem.appendChild(fileName);
        fileItem.appendChild(fileSize);
        fileItem.appendChild(removeBtn);
        
        fileList.appendChild(fileItem);
    });
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    
    if (selectedFiles.length === 0) {
        fileList.classList.add('hidden');
        uploadArea.style.display = 'block';
        addMoreBtn.style.display = 'none';
        checkBtn.disabled = true;
        fileInput.value = '';
        addMoreInput.value = '';
    } else {
        displayFileList();
    }
}

async function checkSyllabi() {
    if (selectedFiles.length === 0) return;

    // Hide sections
    uploadSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
    errorSection.classList.add('hidden');
    loadingSection.classList.remove('hidden');
    
    // Update loading message
    loadingMessage.textContent = selectedFiles.length === 1 
        ? 'Analyzing your syllabus...' 
        : `Analyzing ${selectedFiles.length} syllabi...`;
    progressMessage.textContent = '';

    const formData = new FormData();
    selectedFiles.forEach(file => {
        formData.append('files', file);
    });

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
        showError('An error occurred while checking the syllabi. Please try again.');
    }
}

function showResults(data) {
    resultsSection.classList.remove('hidden');
    
    const individualResults = document.getElementById('individualResults');
    individualResults.innerHTML = '';
    
    // Show batch summary if multiple files
    if (data.batch_stats.total_files > 1) {
        const batchSummary = document.getElementById('batchSummary');
        batchSummary.classList.remove('hidden');
        
        document.getElementById('batchTotal').textContent = data.batch_stats.total_files;
        document.getElementById('batchSuccessful').textContent = data.batch_stats.successful;
        document.getElementById('batchAvgScore').textContent = 
            data.batch_stats.average_required_percentage 
                ? data.batch_stats.average_required_percentage + '%' 
                : 'N/A';
        document.getElementById('batchAvgFound').textContent = 
            data.batch_stats.average_required_found 
                ? data.batch_stats.average_required_found + '/14' 
                : 'N/A';
    } else {
        document.getElementById('batchSummary').classList.add('hidden');
    }
    
    // Display individual results
    data.results.forEach((result, index) => {
        const resultCard = createResultCard(result, index);
        individualResults.appendChild(resultCard);
    });
}

function createResultCard(result, index) {
    const card = document.createElement('div');
    card.className = 'result-card';
    
    // Header
    const header = document.createElement('div');
    header.className = 'result-header';
    
    const title = document.createElement('h3');
    title.innerHTML = `<span class="file-number">#${index + 1}</span> ${result.filename}`;
    
    header.appendChild(title);
    
    // Check if there's an error
    if (result.error) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'result-error';
        errorDiv.innerHTML = `
            <span class="error-icon">⚠️</span>
            <span>${result.error}</span>
        `;
        card.appendChild(header);
        card.appendChild(errorDiv);
        return card;
    }
    
    // Summary stats
    const summaryCard = document.createElement('div');
    summaryCard.className = 'summary-card-mini';
    
    const requiredScore = result.required.percentage;
    const requiredCount = `${result.required.found}/${result.required.total}`;
    
    summaryCard.innerHTML = `
        <div class="summary-stats-mini">
            <div class="stat-mini">
                <div class="stat-value-mini">${requiredScore}%</div>
                <div class="stat-label-mini">Score</div>
            </div>
            <div class="stat-mini">
                <div class="stat-value-mini">${requiredCount}</div>
                <div class="stat-label-mini">Found</div>
            </div>
        </div>
        <div class="summary-status-mini">
            ${getSummaryStatus(requiredScore)}
        </div>
    `;
    
    // Requirements section
    const reqSection = document.createElement('div');
    reqSection.className = 'requirements-details';
    
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'btn-toggle';
    toggleBtn.textContent = 'Show Details';
    toggleBtn.onclick = () => toggleDetails(toggleBtn, detailsDiv);
    
    const detailsDiv = document.createElement('div');
    detailsDiv.className = 'details-content hidden';
    
    // Required items
    const requiredHeader = document.createElement('h4');
    requiredHeader.textContent = 'Required Items';
    detailsDiv.appendChild(requiredHeader);
    
    const requiredContainer = document.createElement('div');
    result.required.items.forEach(item => {
        requiredContainer.appendChild(createRequirementItem(item));
    });
    detailsDiv.appendChild(requiredContainer);
    
    // Recommended items
    const recommendedHeader = document.createElement('h4');
    recommendedHeader.textContent = 'Recommended Items';
    detailsDiv.appendChild(recommendedHeader);
    
    const recommendedContainer = document.createElement('div');
    result.recommended.items.forEach(item => {
        recommendedContainer.appendChild(createRequirementItem(item));
    });
    detailsDiv.appendChild(recommendedContainer);
    
    reqSection.appendChild(toggleBtn);
    reqSection.appendChild(detailsDiv);
    
    // Assemble card
    card.appendChild(header);
    card.appendChild(summaryCard);
    card.appendChild(reqSection);
    
    return card;
}

function getSummaryStatus(score) {
    if (score >= 90) {
        return '🎉 Excellent! Meets most requirements.';
    } else if (score >= 70) {
        return '👍 Good progress! Some items need attention.';
    } else {
        return '⚠️ Several required items appear to be missing.';
    }
}

function toggleDetails(button, detailsDiv) {
    if (detailsDiv.classList.contains('hidden')) {
        detailsDiv.classList.remove('hidden');
        button.textContent = 'Hide Details';
    } else {
        detailsDiv.classList.add('hidden');
        button.textContent = 'Show Details';
    }
}

function createRequirementItem(item) {
    // Check if this is a N/A (not applicable) item
    const isNotApplicable = item.bulletin_check && item.bulletin_check.is_applicable === false;
    
    const div = document.createElement('div');
    div.className = `requirement-item ${isNotApplicable ? 'not-applicable' : (item.found ? 'found' : 'not-found')}`;

    const icon = document.createElement('div');
    icon.className = 'requirement-icon';
    icon.textContent = isNotApplicable ? '—' : (item.found ? '✅' : '❌');

    const content = document.createElement('div');
    content.className = 'requirement-content';

    const name = document.createElement('div');
    name.className = 'requirement-name';
    name.textContent = item.name;

    const confidence = document.createElement('div');
    confidence.className = 'requirement-confidence';
    
    if (isNotApplicable) {
        confidence.textContent = 'N/A - Not applicable for this course';
    } else if (item.has_sub_items) {
        // For items with sub-items, show percentage only
        const percentage = Math.round(item.partial_credit * 100);
        confidence.textContent = `Detected: ${percentage}% complete`;
    } else {
        confidence.textContent = item.found 
            ? `Detected with ${item.confidence}% confidence`
            : `Not detected (${item.confidence}% confidence)`;
    }

    content.appendChild(name);
    content.appendChild(confidence);
    
    // Check if there are any details to show
    const hasDetails = (item.has_sub_items && item.sub_items) || 
                       item.special_note || 
                       (item.bulletin_check && item.bulletin_check.official_text && !item.has_sub_items);
    
    if (hasDetails) {
        // Add toggle button for collapsible details
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'details-toggle';
        toggleBtn.innerHTML = '<span class="toggle-icon">▼</span> Show Details';
        toggleBtn.onclick = () => {
            const isExpanded = detailsContainer.classList.toggle('expanded');
            toggleBtn.innerHTML = isExpanded 
                ? '<span class="toggle-icon">▲</span> Hide Details'
                : '<span class="toggle-icon">▼</span> Show Details';
        };
        
        // Create collapsible container for all details
        const detailsContainer = document.createElement('div');
        detailsContainer.className = 'details-container';
        
        // Add sub-items if available
        if (item.has_sub_items && item.sub_items) {
            const subItemsContainer = document.createElement('div');
            subItemsContainer.className = 'sub-items-container';
            
            item.sub_items.forEach(subItem => {
                const subDiv = document.createElement('div');
                subDiv.className = `sub-item ${subItem.found ? 'found' : 'not-found'}`;
                
                const subIcon = document.createElement('span');
                subIcon.className = 'sub-item-icon';
                subIcon.textContent = subItem.found ? '✓' : '✗';
                
                const subName = document.createElement('span');
                subName.className = 'sub-item-name';
                subName.textContent = subItem.name;
                
                subDiv.appendChild(subIcon);
                subDiv.appendChild(subName);
                
                // Add special note for sub-item if available (e.g., partial title match)
                if (subItem.special_note) {
                    const subSpecialNote = document.createElement('div');
                    subSpecialNote.className = 'sub-item-special-note';
                    subSpecialNote.innerHTML = `<small><span style="color: #f59e0b;">⚠</span> ${subItem.special_note}</small>`;
                    subDiv.appendChild(subSpecialNote);
                }
                
                // Add bulletin check for course title if available
                if (subItem.bulletin_check && subItem.bulletin_check.official_text) {
                    const bulletinNote = document.createElement('div');
                    bulletinNote.className = 'sub-item-bulletin-note';
                    bulletinNote.innerHTML = `<small>Official: "${subItem.bulletin_check.official_text}"</small>`;
                    subDiv.appendChild(bulletinNote);
                }
                
                subItemsContainer.appendChild(subDiv);
            });
            
            detailsContainer.appendChild(subItemsContainer);
        }
        
        // Add special note if available (e.g., final project instead of final exam)
        if (item.special_note) {
            const specialNote = document.createElement('div');
            specialNote.className = 'special-note';
            specialNote.innerHTML = `<span class="info-icon">ℹ️</span> ${item.special_note}`;
            detailsContainer.appendChild(specialNote);
        }
        
        // Add bulletin validation info if available (for non-sub-item requirements)
        if (item.bulletin_check && item.bulletin_check.official_text && !item.has_sub_items) {
            const bulletinInfo = document.createElement('div');
            bulletinInfo.className = isNotApplicable ? 'bulletin-validation na' : 'bulletin-validation';
            
            const bulletinTitle = document.createElement('strong');
            bulletinTitle.textContent = 'Official VCU Bulletin:';
            
            const officialText = document.createElement('p');
            officialText.className = 'official-text';
            officialText.textContent = item.bulletin_check.official_text;
            
            if (!isNotApplicable) {
                const matchStatus = document.createElement('span');
                matchStatus.className = `match-status ${item.bulletin_check.exact_match ? 'exact' : 'no-match'}`;
                matchStatus.textContent = item.bulletin_check.exact_match 
                    ? '✓ Exact match found in syllabus' 
                    : '✗ Official text not found in syllabus';
                
                bulletinInfo.appendChild(bulletinTitle);
                bulletinInfo.appendChild(officialText);
                bulletinInfo.appendChild(matchStatus);
            } else {
                bulletinInfo.appendChild(bulletinTitle);
                bulletinInfo.appendChild(officialText);
            }
            
            detailsContainer.appendChild(bulletinInfo);
        }
        
        content.appendChild(toggleBtn);
        content.appendChild(detailsContainer);
    }

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
    selectedFiles = [];
    fileInput.value = '';
    addMoreInput.value = '';
    fileList.classList.add('hidden');
    uploadArea.style.display = 'block';
    addMoreBtn.style.display = 'none';
    checkBtn.disabled = true;
}
