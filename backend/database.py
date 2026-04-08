import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError(f"Missing env vars: URL={url}, KEY={key[:10] if key else None}")

supabase = create_client(url, key)
