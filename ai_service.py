import os
import json
import google.generativeai as genai

# Add multiple keys to avoid 429 quota errors
API_KEYS = [
    os.getenv("GEMINI_API_KEY_1"),
    os.getenv("GEMINI_API_KEY_2"),
    os.getenv("GEMINI_API_KEY_3"),
]

def get_working_model():
    for key in API_KEYS:
        if not key:
            continue
        try:
            genai.configure(api_key=key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            model.generate_content("test")
            return model
        except Exception as e:
            if "429" in str(e) or "quota" in str(e).lower():
                continue  # Try next key
            raise e
    raise Exception("All API keys exhausted - add more keys")

# 1. Proposal Generator Function
def generate_proposal(job_post: str) -> str:
    model = get_working_model()
    prompt = f"You are an expert freelancer proposal writer. Write a professional, personalized proposal for: {job_post}"
    response = model.generate_content(prompt)
    return response.text

# 2. SEO Gig Optimizer Function
def optimize_gig(title: str, description: str, category: str = "General") -> dict:
    model = get_working_model()
    
    prompt = f""" You are a Fiverr SEO expert. Return JSON only, no extra text.
Category: {category}
Title: {title}
Description: {description}

Return this exact JSON:
{{
  "optimized_title": "under 80 chars",
  "tags": ["tag one", "tag two", "tag three", "tag four", "tag five"],
  "optimized_description": "improved text",
  "scores": {{"title": 8, "tags": 7, "description": 9, "overall": 8}},
  "tips": ["tip 1", "tip 2", "tip 3"]
}}"""

    response = model.generate_content(prompt)
    
    # Strip markdown formatting if Gemini includes it
    raw_text = response.text.replace("```json", "").replace("```", "").strip()
    result = json.loads(raw_text)
    
    # Keyword Tag Validation
    for i, tag in enumerate(result.get("tags", [])):
        words = tag.split()
        result["tags"][i] = {
            "text": tag,
            "valid": 2 <= len(words) <= 5 and len(tag) <= 20
        }
        
    return result

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
    model =  get_working_model()
    response = model.generate_content(
        prompt,
        generation_config={"response_mime_type": "application/json"}
    )
    
    # Parse the raw text string returned by Gemini into a clean Python dictionary
    return json.loads(response.text)
