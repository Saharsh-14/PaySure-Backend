import sys
import os

# Add the project root to sys.path
sys.path.append(os.getcwd())

from app.main import app
from fastapi.routing import APIRoute

def list_routes():
    routes = []
    for route in app.routes:
        if isinstance(route, APIRoute):
            routes.append({
                "path": route.path,
                "name": route.name,
                "methods": list(route.methods)
            })
    
    # Sort by path
    routes.sort(key=lambda x: x["path"])
    
    print(f"{'METHODS':<20} {'PATH':<60} {'NAME'}")
    print("-" * 100)
    for r in routes:
        methods = ", ".join(r["methods"])
        print(f"{methods:<20} {r['path']:<60} {r['name']}")

if __name__ == "__main__":
    list_routes()
