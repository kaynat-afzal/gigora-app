import google.generativeai as genai
import os

genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-pro')

def generate_proposal(job_post: str) -> str:
    response = model.generate_content(
        f"You are an expert freelancer proposal writer. "
        f"Write a professional, personalized proposal for this job: {job_post}. "
        f"Make it compelling, specific, and under 200 words."
    )
    return response.text