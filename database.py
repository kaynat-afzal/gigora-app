from supabase import create_client
import os
from dotenv import load_dotenv

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