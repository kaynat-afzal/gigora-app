import google.generativeai as genai
import os
import json

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

# 3. Improved Day 5 Profile Analyzer Function (Guarantees JSON output)
def analyze_profile(profile_text: str) -> dict:
    prompt = (
        "You are an expert career coach. Analyze the following freelancer profile description. "
        "You must evaluate it and output a JSON object containing the evaluation. "
        "The JSON object must strictly match this exact format:\n\n"
        "{\n"
        "  \"score\": 8,\n"
        "  \"strengths\": [\"Strength point 1\", \"Strength point 2\"],\n"
        "  \"weaknesses\": [\"Weakness point 1\", \"Weakness point 2\"],\n"
        "  \"suggestions\": [\"Suggestion point 1\", \"Suggestion point 2\"]\n"
        "}\n\n"
        f"Profile description to analyze:\n{profile_text}"
    )
    
    # We configure generation_config to force Gemini to output a valid JSON string
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    # Parse the raw text string returned by Gemini into a clean Python dictionary
    return json.loads(response.text)