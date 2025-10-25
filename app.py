from flask import Flask, render_template, request, jsonify
import os
import PyPDF2
import docx
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter
import string
from datetime import datetime
import dateutil.parser as date_parser

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Get the directory of the current file
basedir = os.path.abspath(os.path.dirname(__file__))

# Configure Flask with explicit template and static folders
app = Flask(__name__,
            template_folder=os.path.join(basedir, 'app', 'templates'),
            static_folder=os.path.join(basedir, 'app', 'static'))
app.config['UPLOAD_FOLDER'] = os.path.join(basedir, 'app', 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Extended skill keywords for better matching
SKILL_KEYWORDS = [
    'python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'angular', 
    'node', 'django', 'flask', 'spring', 'aws', 'docker', 'kubernetes',
    'machine learning', 'data analysis', 'project management', 'communication',
    'teamwork', 'leadership', 'problem solving', 'research', 'design',
    'c++', 'c#', 'ruby', 'php', 'swift', 'kotlin', 'go', 'rust',
    'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
    'git', 'jenkins', 'travis ci', 'circle ci', 'github', 'gitlab',
    'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
    'linux', 'ubuntu', 'centos', 'bash', 'shell scripting',
    'agile', 'scrum', 'kanban', 'jira', 'confluence',
    'excel', 'tableau', 'power bi', 'spark', 'hadoop',
    'networking', 'security', 'encryption', 'firewall',
    'api', 'rest', 'graphql', 'soap', 'microservices',
    'testing', 'unit testing', 'integration testing', 'selenium',
    'devops', 'ci/cd', 'terraform', 'ansible', 'puppet',
    'cloud', 'azure', 'gcp', 'firebase', 'heroku',
    'mobile development', 'android', 'ios', 'flutter', 'react native',
    'database design', 'orm', 'hibernate', 'entity framework',
    'ux/ui', 'wireframing', 'prototyping', 'adobe creative suite',
    'seo', 'digital marketing', 'content management', 'wordpress',
    'salesforce', 'sap', 'oracle', 'erp', 'crm',
    'financial analysis', 'risk management', 'accounting', 'auditing',
    'customer service', 'technical support', 'troubleshooting',
    'product management', 'business analysis', 'requirements gathering',
    'quality assurance', 'qa', 'six sigma', 'lean',
    'copywriting', 'technical writing', 'documentation',
    'public speaking', 'presentation', 'negotiation',
    'time management', 'organization', 'multitasking',
    'critical thinking', 'creativity', 'innovation',
    'foreign languages', 'spanish', 'french', 'german', 'chinese',
    'data visualization', 'd3.js', 'chart.js', 'plotly',
    'blockchain', 'cryptocurrency', 'ethereum', 'smart contracts',
    'artificial intelligence', 'natural language processing', 'computer vision',
    'iot', 'embedded systems', 'arduino', 'raspberry pi',
    'cybersecurity', 'penetration testing', 'vulnerability assessment',
    'big data', 'data mining', 'data warehousing',
    'robotics', 'automation', 'control systems',
    'supply chain', 'logistics', 'inventory management',
    'human resources', 'recruitment', 'training',
    'legal', 'compliance', 'regulatory affairs',
    'healthcare', 'clinical research', 'patient care',
    'construction', 'civil engineering', 'structural analysis'
]

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {str(e)}"

def extract_text_from_docx(docx_path):
    """Extract text from DOCX file"""
    try:
        doc = docx.Document(docx_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        return text
    except Exception as e:
        return f"Error reading DOCX: {str(e)}"

def extract_text_from_txt(txt_path):
    """Extract text from TXT file"""
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        return f"Error reading TXT: {str(e)}"

def preprocess_text(text):
    """Clean and preprocess text"""
    # Convert to lowercase
    text = text.lower()
    
    # Remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    
    return filtered_tokens

def extract_skills_from_text(text):
    """Extract skills from text"""
    found_skills = []
    text_lower = text.lower()
    for skill in SKILL_KEYWORDS:
        if skill in text_lower:
            found_skills.append(skill.title())
    return list(set(found_skills))  # Remove duplicates

def parse_date(date_str):
    """Parse date string and return datetime object"""
    try:
        # Handle common date formats
        if date_str.lower() in ['present', 'current', 'now']:
            return datetime.now()
        
        # Try to parse the date
        return date_parser.parse(date_str)
    except:
        return None

def extract_experience_timeline(text):
    """Extract experience timeline from resume text"""
    # Look for work experience sections
    experience_patterns = [
        r'(?:work\s+experience|employment\s+history|professional\s+experience)(?:.*?)(?=(?:education|skills|projects|certifications|awards|references|$))',
        r'(?:employment|work\s+history)(?:.*?)(?=(?:education|skills|projects|certifications|awards|references|$))'
    ]
    
    experience_section = ""
    for pattern in experience_patterns:
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            experience_section = match.group(0)
            break
    
    if not experience_section:
        # If no clear section found, try to find job entries throughout the text
        experience_section = text
    
    # Extract job entries using regex patterns
    job_pattern = r'(?:position|title|job|role):\s*([^\n]+?)(?:\s+at\s+|\s*[-–—]\s*)([^\n]+?)\s*(?:dates?|duration|period):\s*([^\n]+?)(?:\s+to\s+|\s*[-–—]\s*)([^\n]+)'
    job_matches = re.findall(job_pattern, experience_section, re.IGNORECASE)
    
    # Alternative pattern for job entries
    alt_job_pattern = r'([^\n]+?)\s*(?:at|@)\s*([^\n]+?)\s*\(?([^\n]*?(?:\d{4}|\d{1,2}/\d{4}|[a-zA-Z]+\s+\d{4}))[^\n]*?[-–—][^\n]*?([^\n]*?(?:\d{4}|\d{1,2}/\d{4}|[a-zA-Z]+\s+\d{4}|present|current))'
    alt_job_matches = re.findall(alt_job_pattern, experience_section, re.IGNORECASE)
    
    jobs = []
    
    # Process job matches
    for match in job_matches:
        title, company, start_date, end_date = match
        jobs.append({
            'title': title.strip(),
            'company': company.strip(),
            'start_date': start_date.strip(),
            'end_date': end_date.strip()
        })
    
    # Process alternative job matches
    for match in alt_job_matches:
        title, company, start_date, end_date = match
        jobs.append({
            'title': title.strip(),
            'company': company.strip(),
            'start_date': start_date.strip(),
            'end_date': end_date.strip()
        })
    
    # If we couldn't extract structured job data, try a simpler approach
    if not jobs:
        # Look for lines that might contain job information
        lines = experience_section.split('\n')
        for i, line in enumerate(lines):
            # Look for patterns like "Job Title at Company (Date - Date)"
            job_pattern_simple = r'([^\n]+?)\s+(?:at|@)\s+([^\n]+?)\s*\(([^)]+)\)'
            match = re.search(job_pattern_simple, line, re.IGNORECASE)
            if match:
                title, company, dates = match.groups()
                # Try to split dates
                date_parts = re.split(r'\s*[-–—]\s*', dates)
                start_date = date_parts[0] if len(date_parts) > 0 else ""
                end_date = date_parts[1] if len(date_parts) > 1 else ""
                
                jobs.append({
                    'title': title.strip(),
                    'company': company.strip(),
                    'start_date': start_date.strip(),
                    'end_date': end_date.strip()
                })
    
    # Sort jobs by date if possible
    jobs_with_dates = []
    for job in jobs:
        start_date = parse_date(job['start_date'])
        end_date = parse_date(job['end_date']) if job['end_date'].lower() not in ['present', 'current', 'now'] else datetime.now()
        
        if start_date:
            jobs_with_dates.append({
                'title': job['title'],
                'company': job['company'],
                'start_date': job['start_date'],
                'end_date': job['end_date'],
                'start_date_obj': start_date,
                'end_date_obj': end_date
            })
    
    # Sort by start date
    jobs_with_dates.sort(key=lambda x: x['start_date_obj'])
    
    # Calculate employment gaps
    timeline_data = []
    total_experience_months = 0
    employment_gaps = 0
    longest_gap_months = 0
    
    for i, job in enumerate(jobs_with_dates):
        gap_before_months = 0
        if i > 0:
            # Calculate gap between this job and the previous one
            prev_job = jobs_with_dates[i-1]
            gap = (job['start_date_obj'] - prev_job['end_date_obj']).days
            gap_before_months = max(0, gap // 30)  # Convert to months
            
            if gap_before_months > 3:  # Consider it a gap if more than 3 months
                employment_gaps += 1
                longest_gap_months = max(longest_gap_months, gap_before_months)
        
        timeline_data.append({
            'title': job['title'],
            'company': job['company'],
            'start_date': job['start_date'],
            'end_date': job['end_date'],
            'gap_before_months': gap_before_months
        })
        
        # Calculate experience duration for this job
        duration = (job['end_date_obj'] - job['start_date_obj']).days
        total_experience_months += max(0, duration // 30)
    
    if timeline_data:
        return {
            'jobs': timeline_data,
            'total_experience_years': round(total_experience_months / 12, 1),
            'employment_gaps_count': employment_gaps,
            'longest_gap_months': longest_gap_months
        }
    
    return None

def analyze_resume(text):
    """Analyze resume text and extract insights"""
    # Preprocess text
    tokens = preprocess_text(text)
    
    # Word frequency analysis
    word_freq = Counter(tokens)
    most_common_words = dict(word_freq.most_common(20))
    
    # Extract potential skills
    found_skills = extract_skills_from_text(text)
    
    # Estimate experience (simple word count approach)
    word_count = len(tokens)
    experience_estimate = min(round(word_count / 100), 10)  # Simple heuristic
    
    # Extract contact information (simplified)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(?:\+?(\d{1,3}))?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    # Extract experience timeline
    experience_timeline = extract_experience_timeline(text)
    
    return {
        'word_count': len(tokens),
        'most_common_words': most_common_words,
        'skills': found_skills,
        'experience_estimate': experience_estimate,
        'contact_info': {
            'emails': emails[:3],  # Limit to first 3 emails
            'phones': [''.join(phone) for phone in phones[:3]]  # Limit to first 3 phones
        },
        'experience_timeline': experience_timeline
    }

def analyze_skills_match(resume_skills, job_description):
    """Compare resume skills with job description and calculate match score"""
    if not job_description.strip():
        return None
    
    # Extract skills from job description
    job_skills = extract_skills_from_text(job_description)
    
    if not job_skills:
        return None
    
    # Calculate match score
    matching_skills = set(resume_skills) & set(job_skills)
    missing_skills = set(job_skills) - set(resume_skills)
    
    match_score = int((len(matching_skills) / len(job_skills)) * 100)
    
    return {
        'match_score': match_score,
        'matching_skills': list(matching_skills),
        'missing_skills': list(missing_skills),
        'matching_skills_count': len(matching_skills),
        'missing_skills_count': len(missing_skills),
        'total_job_skills': len(job_skills)
    }

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    """Handle resume analysis request"""
    if 'resume' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['resume']
    job_description = request.form.get('job_description', '')
    
    if file.filename is None or file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file:
        # Get file extension
        file_ext = os.path.splitext(file.filename)[1].lower() if file.filename else ''
        
        # Save file temporarily
        filename = file.filename if file.filename else 'uploaded_file'
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Extract text based on file type
        text = ""
        if file_ext == '.pdf':
            text = extract_text_from_pdf(filepath)
        elif file_ext in ['.docx', '.doc']:
            text = extract_text_from_docx(filepath)
        elif file_ext == '.txt':
            text = extract_text_from_txt(filepath)
        else:
            # Clean up temporary file
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': 'Unsupported file format. Please upload PDF, DOCX, or TXT files.'}), 400
        
        # Analyze the resume
        analysis_result = analyze_resume(text)
        
        # Analyze skills match if job description is provided
        if job_description:
            skills_match = analyze_skills_match(analysis_result['skills'], job_description)
            if skills_match:
                analysis_result['skills_match'] = skills_match
        
        # Clean up temporary file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify(analysis_result)
    
    return jsonify({'error': 'Invalid request'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
