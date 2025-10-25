document.addEventListener('DOMContentLoaded', function() {
    // Get DOM elements
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const browseBtn = document.getElementById('browseBtn');
    const fileInfo = document.getElementById('fileInfo');
    const fileName = document.getElementById('fileName');
    const removeFile = document.getElementById('removeFile');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsSection = document.getElementById('resultsSection');
    const loading = document.getElementById('loading');
    const errorMessage = document.getElementById('errorMessage');
    const errorMessageText = document.getElementById('errorMessageText');
    
    let selectedFile = null;
    
    // Event listeners for file selection
    browseBtn.addEventListener('click', () => {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', handleFileSelect);
    
    // Drag and drop events
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('drag-over');
    });
    
    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        if (e.dataTransfer.files.length) {
            handleFiles(e.dataTransfer.files);
        }
    });
    
    // Remove file event
    removeFile.addEventListener('click', () => {
        resetFileSelection();
    });
    
    // Analyze button event
    analyzeBtn.addEventListener('click', analyzeResume);
    
    // Handle file selection
    function handleFileSelect(e) {
        if (e.target.files.length) {
            handleFiles(e.target.files);
        }
    }
    
    // Process selected files
    function handleFiles(files) {
        const file = files[0];
        
        // Check file type
        const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
        const fileExt = file.name.split('.').pop().toLowerCase();
        const validExtensions = ['pdf', 'docx', 'txt'];
        
        if (!validExtensions.includes(fileExt)) {
            showError('Please select a valid file (PDF, DOCX, or TXT)');
            return;
        }
        
        // Check file size (max 16MB)
        if (file.size > 16 * 1024 * 1024) {
            showError('File size exceeds 16MB limit');
            return;
        }
        
        selectedFile = file;
        fileName.textContent = file.name;
        fileInfo.style.display = 'flex';
        analyzeBtn.disabled = false;
        hideError();
    }
    
    // Reset file selection
    function resetFileSelection() {
        selectedFile = null;
        fileInput.value = '';
        fileInfo.style.display = 'none';
        analyzeBtn.disabled = true;
    }
    
    // Analyze resume
    function analyzeResume() {
        if (!selectedFile) {
            showError('Please select a file first');
            return;
        }
        
        // Show loading indicator
        loading.style.display = 'block';
        resultsSection.style.display = 'none';
        hideError();
        
        // Create FormData object
        const formData = new FormData();
        formData.append('resume', selectedFile);
        
        // Send AJAX request
        fetch('/analyze', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            loading.style.display = 'none';
            
            if (data.error) {
                showError(data.error);
            } else {
                displayResults(data);
            }
        })
        .catch(error => {
            loading.style.display = 'none';
            showError('An error occurred while analyzing the resume. Please try again.');
            console.error('Error:', error);
        });
    }
    
    // Display analysis results
    function displayResults(data) {
        // Update summary section
        document.getElementById('wordCount').textContent = data.word_count;
        document.getElementById('experienceLevel').textContent = `${data.experience_estimate} years`;
        document.getElementById('skillsCount').textContent = data.skills.length;
        
        // Update contact information
        const emailsElement = document.getElementById('emails');
        if (data.contact_info.emails && data.contact_info.emails.length > 0) {
            emailsElement.textContent = data.contact_info.emails.join(', ');
        } else {
            emailsElement.textContent = 'None found';
        }
        
        const phonesElement = document.getElementById('phones');
        if (data.contact_info.phones && data.contact_info.phones.length > 0) {
            phonesElement.textContent = data.contact_info.phones.join(', ');
        } else {
            phonesElement.textContent = 'None found';
        }
        
        // Populate keywords
        const keywordsContainer = document.getElementById('keywordsContainer');
        keywordsContainer.innerHTML = '';
        
        if (data.most_common_words) {
            Object.entries(data.most_common_words).forEach(([word, count]) => {
                const keywordTag = document.createElement('span');
                keywordTag.className = 'keyword-tag';
                keywordTag.textContent = `${word} (${count})`;
                keywordsContainer.appendChild(keywordTag);
            });
        }
        
        // Populate skills
        const skillsContainer = document.getElementById('skillsContainer');
        skillsContainer.innerHTML = '';
        
        if (data.skills && data.skills.length > 0) {
            data.skills.forEach(skill => {
                const skillTag = document.createElement('span');
                skillTag.className = 'skill-tag';
                skillTag.textContent = skill;
                skillsContainer.appendChild(skillTag);
            });
        } else {
            const noSkills = document.createElement('p');
            noSkills.textContent = 'No skills detected';
            skillsContainer.appendChild(noSkills);
        }
        
        // Show results section
        resultsSection.style.display = 'block';
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Show error message
    function showError(message) {
        errorMessageText.textContent = message;
        errorMessage.style.display = 'block';
        errorMessage.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Hide error message
    function hideError() {
        errorMessage.style.display = 'none';
    }
});