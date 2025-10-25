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
    const jobDescription = document.getElementById('jobDescription');
    
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
        formData.append('job_description', jobDescription.value);
        
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
        
        // Display experience timeline if available
        const timelineSection = document.getElementById('timelineSection');
        if (data.experience_timeline) {
            timelineSection.style.display = 'block';
            displayTimeline(data.experience_timeline);
        } else {
            timelineSection.style.display = 'none';
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
        
        // Display skills match analysis if available
        const skillsMatchSection = document.getElementById('skillsMatchSection');
        if (data.skills_match) {
            skillsMatchSection.style.display = 'block';
            document.getElementById('matchScore').textContent = `${data.skills_match.match_score}%`;
            document.getElementById('matchingSkills').textContent = data.skills_match.matching_skills_count;
            document.getElementById('missingSkills').textContent = data.skills_match.missing_skills_count;
            
            // Populate missing skills
            const missingSkillsContainer = document.getElementById('missingSkillsContainer');
            missingSkillsContainer.innerHTML = '<h4>Recommended Skills to Add:</h4>';
            
            if (data.skills_match.missing_skills && data.skills_match.missing_skills.length > 0) {
                const missingSkillsList = document.createElement('div');
                missingSkillsList.className = 'skills-container';
                
                data.skills_match.missing_skills.forEach(skill => {
                    const skillTag = document.createElement('span');
                    skillTag.className = 'skill-tag';
                    skillTag.textContent = skill;
                    missingSkillsList.appendChild(skillTag);
                });
                
                missingSkillsContainer.appendChild(missingSkillsList);
            } else {
                const noMissingSkills = document.createElement('p');
                noMissingSkills.textContent = 'No missing skills found!';
                missingSkillsContainer.appendChild(noMissingSkills);
            }
        } else {
            skillsMatchSection.style.display = 'none';
        }
        
        // Show results section
        resultsSection.style.display = 'block';
        
        // Scroll to results
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }
    
    // Display experience timeline
    function displayTimeline(timelineData) {
        const timelineContainer = document.getElementById('experienceTimeline');
        timelineContainer.innerHTML = '';
        
        // Create timeline entries
        timelineData.jobs.forEach((job, index) => {
            const entry = document.createElement('div');
            entry.className = 'timeline-entry';
            
            const badge = document.createElement('div');
            badge.className = 'timeline-badge';
            badge.textContent = index + 1;
            
            const panel = document.createElement('div');
            panel.className = 'timeline-panel';
            
            const title = document.createElement('h4');
            title.textContent = job.title;
            
            const company = document.createElement('div');
            company.className = 'company';
            company.textContent = job.company;
            
            const duration = document.createElement('div');
            duration.className = 'duration';
            duration.textContent = `${job.start_date} - ${job.end_date}`;
            
            panel.appendChild(title);
            panel.appendChild(company);
            panel.appendChild(duration);
            
            // Add gap warning if this job has an employment gap before it
            if (job.gap_before_months && job.gap_before_months > 3) {
                const gapWarning = document.createElement('div');
                gapWarning.className = 'gap-warning';
                gapWarning.textContent = `Employment gap: ${job.gap_before_months} months`;
                panel.appendChild(gapWarning);
            }
            
            entry.appendChild(badge);
            entry.appendChild(panel);
            timelineContainer.appendChild(entry);
        });
        
        // Display timeline summary
        const summaryContainer = document.getElementById('timelineSummary');
        summaryContainer.innerHTML = '<h4>Career Summary</h4>';
        
        const summaryGrid = document.createElement('div');
        summaryGrid.className = 'summary-grid';
        
        const totalExperienceItem = document.createElement('div');
        totalExperienceItem.className = 'summary-item';
        totalExperienceItem.innerHTML = '<span class="label">Total Experience</span><span class="value">' + timelineData.total_experience_years + ' years</span>';
        
        const employmentGapsItem = document.createElement('div');
        employmentGapsItem.className = 'summary-item';
        employmentGapsItem.innerHTML = '<span class="label">Employment Gaps</span><span class="value">' + timelineData.employment_gaps_count + '</span>';
        
        const longestGapItem = document.createElement('div');
        longestGapItem.className = 'summary-item';
        longestGapItem.innerHTML = '<span class="label">Longest Gap</span><span class="value">' + timelineData.longest_gap_months + ' months</span>';
        
        summaryGrid.appendChild(totalExperienceItem);
        summaryGrid.appendChild(employmentGapsItem);
        summaryGrid.appendChild(longestGapItem);
        summaryContainer.appendChild(summaryGrid);
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
