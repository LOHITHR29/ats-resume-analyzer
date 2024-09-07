import os
from dotenv import load_dotenv
import streamlit as st
import google.generativeai as genai
import PyPDF2 as pdf
import json
import base64

load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")

if not api_key:
    st.error("Google API Key is missing. Please set the GOOGLE_API_KEY environment variable.")
    st.write("To set the environment variable:")
    st.code("1. Create a .env file in your project directory")
    st.code("2. Add the following line to the .env file:")
    st.code("GOOGLE_API_KEY=your_actual_api_key_here")
    st.write("3. Restart your Streamlit app")
    st.stop()

genai.configure(api_key=api_key)

def get_gemini_response(input):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(input)
    return response.text

def extract_text_from_pdf(file):
    reader = pdf.PdfReader(file)
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    return text

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{os.path.basename(bin_file)}">Download {file_label}</a>'
    return href

analysis_prompt = """
Hey, act like a best expert in ATS with deep knowledge of resumes in fields like machine learning, data science, AI, etc. Your task is to evaluate the resume based on the job description and give the resume a score out of 100. Also, provide ATS keywords that are most relevant to the job description that need to be added to the resume to make it more relevant to the job description.

Resume: {text}
Job Description: {job_description}

I want the response in one single string having the structure:
{{"JD_matchscore":"%","Missing_keywords":"","Relevant_keywords":"","Profile_summary":"","Score":""}}
"""

improvement_prompt = """
Based on the following resume and job description, create an improved version of the resume that would score at least 75% match with the job description. Focus on highlighting relevant experience, skills, and achievements that align with the job requirements. Ensure the improved resume maintains a professional tone and structure.

Original Resume:
{original_resume}

Job Description:
{job_description}

Previous Analysis:
{previous_analysis}

Please provide the improved resume in a clear, well-structured format suitable for an ATS system.
"""

st.set_page_config(page_title="Smart ATS Resume Analyzer", layout="wide")

st.title("Smart ATS Resume Analyzer")
st.markdown("Improve your resume's ATS score and stand out from the crowd!")

col1, col2 = st.columns(2)

with col1:
    jd = st.text_area("Paste the Job Description", height=300)

with col2:
    uploaded_file = st.file_uploader("Upload Your Resume (PDF)", type="pdf")

if st.button("Analyze and Improve Resume", key="submit"):
    if uploaded_file is not None and jd:
        with st.spinner("Analyzing your resume..."):
            original_resume = extract_text_from_pdf(uploaded_file)
            analysis_prompt_formatted = analysis_prompt.format(text=original_resume, job_description=jd)
            try:
                analysis_response = get_gemini_response(analysis_prompt_formatted)
                analysis_dict = json.loads(analysis_response)
                current_score = float(analysis_dict["Score"])

                st.subheader("Initial Analysis Result")
                col1, col2, col3 = st.columns(3)
                col1.metric("Match Score", f"{analysis_dict['JD_matchscore']}")
                col2.metric("ATS Score", f"{current_score}/100")
                col3.json(analysis_response)

                if current_score < 75:
                    st.warning("Your current resume score is below 75%. Let's improve it!")
                    with st.spinner("Generating improved resume..."):
                        improvement_prompt_formatted = improvement_prompt.format(
                            original_resume=original_resume,
                            job_description=jd,
                            previous_analysis=analysis_response
                        )
                        improved_resume = get_gemini_response(improvement_prompt_formatted)
                        
                        st.subheader("Improved Resume Suggestion")
                        st.text_area("Improved Resume", improved_resume, height=400)
                        
                        with open("improved_resume.txt", "w") as f:
                            f.write(improved_resume)
                        
                        st.markdown(get_binary_file_downloader_html("improved_resume.txt", "Improved Resume"), unsafe_allow_html=True)

                        analysis_prompt_improved = analysis_prompt.format(text=improved_resume, job_description=jd)
                        improved_analysis_response = get_gemini_response(analysis_prompt_improved)
                        improved_analysis_dict = json.loads(improved_analysis_response)
                        improved_score = float(improved_analysis_dict["Score"])

                        st.subheader("Improved Resume Analysis")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("New Match Score", f"{improved_analysis_dict['JD_matchscore']}", f"{float(improved_analysis_dict['JD_matchscore'][:-1]) - float(analysis_dict['JD_matchscore'][:-1]):.1f}%")
                        col2.metric("New ATS Score", f"{improved_score}/100", f"{improved_score - current_score:.1f}")
                        col3.json(improved_analysis_response)
                else:
                    st.success(f"Great job! Your resume already scores {current_score}/100, which is above the 75% threshold.")

            except Exception as e:
                st.error(f"An error occurred while processing your request: {str(e)}")
                st.write("Please check your API key and try again.")
    else:
        st.warning("Please upload a PDF resume and provide a job description before submitting.")

st.markdown("---")
st.markdown("Made with ❤️ by LohithRegalla")