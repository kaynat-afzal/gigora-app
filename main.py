from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware  # <-- Add this import
from ai_service import generate_proposal, optimize_gig, analyze_profile
from database import supabase, get_stats, check_and_increment_usage
from pydantic import BaseModel
from datetime import date
from pydantic import BaseModel

app = FastAPI(title="Gigora API")
# Enable CORS so the React frontend can talk to your backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all frontend development servers (like http://localhost:3000)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- Pydantic Data Models (Defined first so they are recognized below) ---

class AuthModel(BaseModel):
    email: str
    password: str

class ProposalRequest(BaseModel):
    job_post: str
    tone: str = "professional"
    skill: str = "Web Dev"
    platform: str = "Upwork"
    length: str = "medium"

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

async def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not logged in")
    
    token = authorization.replace("Bearer ", "")
    try:
        user_resp = supabase.auth.get_user(token)
        user_id = user_resp.user.id
        
        # Get user details from profiles table
        user_data = supabase.table("profiles").select("*").eq("id", user_id).execute()
        
        if user_data.data:
            return user_data.data[0]
        
        # Fallback if profile row doesn't exist yet
        return {"id": user_id, "email": user_resp.user.email, "plan": "free"}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
# --- Day 4 AI Engine Endpoints ---

@app.post("/api/proposal")
def create_proposal(data: ProposalRequest, current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    plan = current_user.get("plan", "free")
    
    usage = check_and_increment_usage(user_id, plan)
    if not usage["allowed"]:
        raise HTTPException(status_code=429, detail="Daily limit reached! Upgrade to Pro.")

    # ... rest of your proposal generation code ...

    # --- 2. YOUR EXISTING AI CODE ---
    
    try:
        # 1. Generate the proposal using Gemini
        proposal = generate_proposal(
    job_post=data.job_post,
    tone=data.tone,
    skill=data.skill,
    platform=data.platform,
    length=data.length)
        
        # 2. Save the details directly to the Supabase 'proposals' table
        supabase.table("proposals").insert({
            "job_post": data.job_post,
            "proposal": proposal
        }).execute()
        
        # 3. Return the proposal to the frontend
        return {"proposal": proposal}
    except Exception as e:
        # Proper error handling: returns a clean, descriptive message
        raise HTTPException(status_code=500, detail=f"Database or AI Error: {str(e)}")

# Request body model
class SEORequest(BaseModel):
    title: str
    description: str
    category: str = "General"

@app.post("/api/seo")
def handle_seo_optimization(data: SEORequest):
    return optimize_gig(data.title, data.description, data.category)

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
@app.get("/api/history")
def get_user_history(user_id: str):
    try:
        response = supabase.table("history").select("*").eq("user_id", user_id).order("created_at", desc=True).limit(20).execute()
        return {"history": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/history/{item_id}")
def delete_history_item(item_id: int):
    try:
        supabase.table("history").delete().eq("id", item_id).execute()
        return {"message": "History item deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
def get_user_stats(user_id: str):
    try:
        return get_stats(user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/api/usage")
def get_user_usage(user_id: str, plan: str = "free"):
    try:
        today = str(date.today())
        result = supabase.table("usage").select("count").eq("user_id", user_id).eq("date", today).execute()
        current = result.data[0]["count"] if result.data else 0

        if plan == "pro":
            return {"remaining": 999, "used": current, "limit": "unlimited"}

        return {"remaining": max(0, 5 - current), "used": current, "limit": 5}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/api/me")
def get_user_profile(current_user: dict = Depends(get_current_user)):
    try:
        user_id = current_user.get("id")
        plan = current_user.get("plan", "free")
        
        # Get stats/usage
        usage = check_and_increment_usage(user_id, plan)
        
        return {
            "user": current_user,
            "usage": usage
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))