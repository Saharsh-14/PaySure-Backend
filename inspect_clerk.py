import urllib.request
import json
import os
from app.core.config import settings

def inspect_clerk_users():
    try:
        clerk_base = "https://api.clerk.com"
        clerk_url = f"{clerk_base}/v1/users?limit=10"
        req = urllib.request.Request(clerk_url)
        req.add_header("Authorization", f"Bearer {settings.CLERK_SECRET_KEY}")
        req.add_header("User-Agent", "curl/7.68.0")
        
        with urllib.request.urlopen(req) as response:
            users = json.loads(response.read().decode())
            for u in users:
                email = u.get("email_addresses", [{}])[0].get("email_address")
                pub = u.get("public_metadata", {})
                un = u.get("unsafe_metadata", {})
                print(f"User: {email}")
                print(f"  Public Metadata: {pub}")
                print(f"  Unsafe Metadata: {un}")
                print("-" * 20)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_clerk_users()
