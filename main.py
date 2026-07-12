from fastapi import FastAPI, HTTPException
from ai_service import generate_proposal
from database import supabase
from pydantic import BaseModel

app = FastAPI()

# Schema for incoming Auth data (Day 3)
class AuthModel(BaseModel):
    email: str
    password: str

@app.get("/")
def read_root():
    return {"message": "Gigora backend is officially up and running!"}

@app.get("/gigs")
def get_gigs():
    try:
        # Note: Keeps 'tittle' column to perfectly match your database schema
        response = supabase.table("gigs").select("id, tittle, description, price").execute()
        return {"gigs": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/gigs")
def create_gig(title: str, description: str, price: int):
    try:
        new_gig = {
            "tittle": title,  # Keeps 'tittle' exactly as it is in your database table
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

@app.post("/generate-proposal")
def create_proposal(job_post: str):
    proposal = generate_proposal(job_post)
    return {"proposal": proposal}

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