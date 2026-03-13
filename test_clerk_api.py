import urllib.request
import json
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("CLERK_SECRET_KEY")

def test_clerk_api(url):
    print(f"Testing URL: {url}")
    try:
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {SECRET_KEY}")
        req.add_header("User-Agent", "Python-urllib/3.10")
        with urllib.request.urlopen(req, timeout=10) as response:
            print(f"SUCCESS: {response.getcode()}")
            # print(response.read()[:200])
    except Exception as e:
        print(f"FAILED: {e}")

test_clerk_api("https://api.clerk.com/v1/users?limit=1")
test_clerk_api("https://summary-lioness-53.clerk.accounts.dev/v1/users?limit=1")
