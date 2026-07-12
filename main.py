import os
from fastapi import FastAPI
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables from your .env file
load_dotenv()

app = FastAPI()

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_ANON_KEY")

# Initialize the Supabase client
supabase: Client = create_client(url, key)

@app.get("/")
def read_root():
    return {"message": "Gigora backend is officially up and running!", "database_connected": supabase is not None}# Fetch all gigs from your new Supabase table
@app.get("/gigs")
def get_gigs():
    try:
        # Note: Using 'tittle' to match the column name in your screenshot
        response = supabase.table("gigs").select("id, tittle, description, price").execute()
        return {"gigs": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))# Create a new gig route
@app.post("/gigs")
def create_gig(tittle: str, description: str, price: int):
    try:
        new_gig = {
            "tittle": tittle,
            "description": description,
            "price": price
        }
        response = supabase.table("gigs").insert(new_gig).execute()
        return {"message": "Gig added successfully!", "data": response.data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))# Day 2 Task: Health check endpoint
@app.get("/api/health")
def health_check():
    return {"status": "ok", "message": "Gigora API is running perfectly"}