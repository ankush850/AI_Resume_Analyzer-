# AI Resume Analyzer

An intelligent resume analysis tool that helps job seekers optimize their resumes by extracting key insights and providing actionable feedback.

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/flask-2.3.2-green)
![License](https://img.shields.io/badge/license-MIT-blue)

## Features

- **Multi-format Support**: Upload resumes in PDF, DOCX, or TXT formats
- **Text Analysis**: Extracts and analyzes text content from resumes
- **Keyword Identification**: Finds the most frequently used words and phrases
- **Skill Detection**: Identifies technical and soft skills from a comprehensive keyword database
- **Experience Estimation**: Provides a heuristic-based estimate of professional experience
- **Contact Information Extraction**: Automatically finds emails and phone numbers
- **Clean UI**: Modern, responsive interface with drag-and-drop file upload
- **Real-time Analysis**: Instant feedback on resume content

## Technology Stack

- **Backend**: Python, Flask
- **Text Processing**: NLTK, PyPDF2, python-docx
- **Frontend**: HTML, CSS, JavaScript
- **NLP Libraries**: NLTK for text preprocessing and analysis

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Steps

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd ai-resume-analyzer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies (use `--timeout 1000` if you experience network issues):
   ```bash
   pip install -r requirements.txt
   ```
   
   The requirements include:
   ```
   flask==2.3.2
   python-docx==0.8.11
   PyPDF2==3.0.1
   nltk==3.8.1
   scikit-learn==1.3.0
   pandas==2.0.3
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Access the application at `http://127.0.0.1:5000`

## Usage

1. Navigate to the application in your web browser
2. Upload your resume using the drag-and-drop interface or file browser
3. Click "Analyze Resume" to process your document
4. Review the analysis results including:
   - Word count and experience estimate
   - Identified skills
   - Contact information
   - Top keywords from your resume

## Analysis Capabilities

- **Text Preprocessing**: Removes punctuation, converts to lowercase, and filters stop words
- **Word Frequency Analysis**: Identifies the most common terms in your resume
- **Skill Matching**: Detects skills from a predefined list of technical and soft skills
- **Contact Information Extraction**: Finds email addresses and phone numbers using regex patterns

## Project Structure

```
ai-resume-analyzer/
├── app/
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   ├── js/
│   │   │   └── script.js
│   │   └── uploads/ (created automatically)
│   └── templates/
│       └── index.html
├── app.py
├── requirements.txt
└── README.md
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create a new branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Future Enhancements

- Job description matching and compatibility scoring
- Resume improvement suggestions
- Export analysis results to PDF
- Multi-language support
- Industry-specific analysis
- ATS (Applicant Tracking System) compatibility checking

## Troubleshooting

### Network Issues During Installation

If you experience timeout errors during package installation, try using the `--timeout` flag:

```bash
pip install --timeout 1000 -r requirements.txt
```

### Template Not Found Error

If you encounter a "TemplateNotFound" error, ensure that the Flask app is correctly configured to find the templates directory. The application should automatically locate templates in the `app/templates` directory.

### NLTK Data Download

On first run, the application will automatically download required NLTK data. If this fails, you can manually download it by running:

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
```