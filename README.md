# ATS Resume Analyzer

This project is a Streamlit web application that analyzes resumes against job descriptions using AI to provide ATS (Applicant Tracking System) scores and suggestions for improvement.

## Features

- Upload PDF resumes
- Input job descriptions
- Analyze resume-job description match
- Provide ATS score and relevant keywords
- Generate improved resume suggestions
- Download improved resume

## Setup

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up a `.env` file with your Google API key: `GOOGLE_API_KEY=your_api_key_here`
4. Run the app: `streamlit run app.py`

## Usage

1. Enter a job description
2. Upload a PDF resume
3. Click "Analyze and Improve Resume"
4. View analysis results and improved resume suggestion
5. Download the improved resume if desired

## Technologies Used

- Python
- Streamlit
- Google Generative AI (Gemini Pro)
- PyPDF2

## Author

Lohith Regalla
