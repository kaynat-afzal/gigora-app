import google.generativeai as genai
import os

# Configure the Gemini API client
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

# 1. Proposal Generator Function
def generate_proposal(job_post: str) -> str:
    prompt = (
        "You are an expert freelancer proposal writer. "
        f"Write a professional, personalized proposal for this job: {job_post}. "
        "Make it compelling, specific, and under 200 words."
    )
    response = model.generate_content(prompt)
    return response.text

# 2. SEO Gig Optimizer Function
def optimize_gig(title: str, description: str) -> str:
    prompt = (
        "You are an SEO expert specializing in freelance gig marketplaces. "
        f"Analyze this gig Title: '{title}' and Description: '{description}'. "
        "Provide a highly optimized version of both the title and description to maximize search visibility, "
        "and suggest 5 high-traffic search tags."
    )
    response = model.generate_content(prompt)
    return response.text

# 3. Profile Analyzer Function
def analyze_profile(profile_text: str) -> str:
    prompt = (
        "You are a professional career coach. "
        f"Analyze this freelancer profile text:\n{profile_text}\n\n"
        "Provide constructive feedback on: \n"
        "1. Strengths\n"
        "2. Areas of improvement\n"
        "3. Recommended skills or wording adjustments to attract high-paying clients."
    )
    response = model.generate_content(prompt)
    return response.text