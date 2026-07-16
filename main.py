from fastapi import FastAPI, HTTPException
from ai_service import generate_proposal, optimize_gig, analyze_profile
from database import supabase
from pydantic import BaseModel

app = FastAPI()

# --- Pydantic Data Models (Defined first so they are recognized below) ---

class AuthModel(BaseModel):
    email: str
    password: str

class ProposalRequest(BaseModel):
    job_post: str

class SEORequest(BaseModel):
    title: str
    description: str

class ProfileRequest(BaseModel):
    profile_text: str


# --- Core App Endpoints ---

@app.get("/")
def read_root():
    return {"message": "Gigora backend is officially up and running!"}

@app.get("/gigs")
def get_gigs():
    try:
        response = supabase.table("gigs").select("id, tittle, description, price").execute()
        return {"gigs": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gigs")
def create_gig(title: str, description: str, price: int):
    try:
        new_gig = {
            "tittle": title,  # Matches 'tittle' column in your Supabase DB
            "description": description,
            "price": price
        }
        response = supabase.table("gigs").insert(new_gig).execute()
        return {"message": "Gig added successfully!", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Gigora API is running perfectly"}


# --- Day 4 AI Engine Endpoints ---

@app.post("/api/proposal")
def create_proposal(data: ProposalRequest):
    try:
        proposal = generate_proposal(data.job_post)
        return {"proposal": proposal}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/seo")
def optimize_gig_endpoint(data: SEORequest):
    try:
        optimized_result = optimize_gig(data.title, data.description)
        return {"optimized": optimized_result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/profile")
def analyze_profile_endpoint(data: ProfileRequest):
    try:
        # This will now receive a dictionary directly!
        analysis = analyze_profile(data.profile_text)
        return {"analysis": analysis}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# --- Day 3 Authentication Endpoints ---

@app.post("/api/auth/signup")
def signup(data: AuthModel):
    try:
        response = supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })
        return {"message": "Signup successful!", "user": response.user}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/auth/login")
def login(data: AuthModel):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
        return {"message": "Login successful!", "session": response.session}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))