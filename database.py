from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import date

load_dotenv()

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")
)
def save_history(user_id: str, type: str, input_text: str, output: str):
    supabase.table("history").insert({
        "user_id": user_id,
        "type": type,
        "input_text": input_text[:500],  # limit storage length if needed
        "output": str(output)
    }).execute()

def get_stats(user_id: str) -> dict:
    result = supabase.table("history").select("type").eq("user_id", user_id).execute()
    data = result.data
    return {
        "proposals": len([x for x in data if x["type"] == "proposal"]),
        "seo": len([x for x in data if x["type"] == "seo"]),
        "profiles": len([x for x in data if x["type"] == "profile"]),
        "total": len(data)
    }
    from datetime import date

def check_and_increment_usage(user_id: str, plan: str = "free") -> dict:
    # Pro users get unlimited access
    if plan == "pro":
        return {"allowed": True, "remaining": 999, "used": 0}
    
    today = str(date.today())
    
    # Check current usage for today
    result = supabase.table("usage").select("count").eq("user_id", user_id).eq("date", today).execute()
    current = result.data[0]["count"] if result.data else 0
    
    # Block if 5 or more uses reached
    if current >= 5:
        return {"allowed": False, "remaining": 0, "used": current}
    
    # Increment usage
    if result.data:
        supabase.table("usage").update({"count": current + 1}).eq("user_id", user_id).eq("date", today).execute()
    else:
        supabase.table("usage").insert({"user_id": user_id, "date": today, "count": 1}).execute()
        
    return {"allowed": True, "remaining": 5 - (current + 1), "used": current + 1}