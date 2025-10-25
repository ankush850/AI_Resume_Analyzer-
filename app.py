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

def analyze_resume(text):
    """Analyze resume text and extract insights"""
    # Preprocess text
    tokens = preprocess_text(text)
    
    # Word frequency analysis
    word_freq = Counter(tokens)
    most_common_words = dict(word_freq.most_common(20))
    
    # Extract potential skills (simplified approach)
    skill_keywords = [
        'python', 'java', 'javascript', 'html', 'css', 'sql', 'react', 'angular', 
        'node', 'django', 'flask', 'spring', 'aws', 'docker', 'kubernetes',
        'machine learning', 'data analysis', 'project management', 'communication',
        'teamwork', 'leadership', 'problem solving', 'research', 'design'
    ]
    
    found_skills = []
    text_lower = text.lower()
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill.title())
    
    # Estimate experience (simple word count approach)
    word_count = len(tokens)
    experience_estimate = min(round(word_count / 100), 10)  # Simple heuristic
    
    # Extract contact information (simplified)
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    phone_pattern = r'(?:\+?(\d{1,3}))?[-.\s]?\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})'
    
    emails = re.findall(email_pattern, text)
    phones = re.findall(phone_pattern, text)
    
    return {
        'word_count': len(tokens),
        'most_common_words': most_common_words,
        'skills': found_skills,
        'experience_estimate': experience_estimate,
        'contact_info': {
            'emails': emails[:3],  # Limit to first 3 emails
            'phones': [''.join(phone) for phone in phones[:3]]  # Limit to first 3 phones
        }
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
        
        # Clean up temporary file
        if os.path.exists(filepath):
            os.remove(filepath)
        
        return jsonify(analysis_result)
    
    return jsonify({'error': 'Invalid request'}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)