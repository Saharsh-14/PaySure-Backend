from fastapi import FastAPI, Request
import time
from app.api import projects
from app.api import transaction
from app.api import disputes
from app.api import wallet
from app.api import admin
from app.api import webhooks
from app.api import milestones
from app.api import connections
from app.api import users
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.core.rate_limiter import limiter
from app.core.logger import logger
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi import Depends
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import get_db

app = FastAPI(
    title="PaySure API",
    description="""
**Clerk Authentication Integration**

This API is secured using Clerk JWT verification. 
- All protected endpoints require a valid Clerk JWT passed in the `Authorization: Bearer <token>` header.
- User identity is extracted from the `sub` claim (`clerk_id`).
- Role-based Access Control (RBAC) relies on roles defined in the user's `public_metadata`.
- The database does NOT store user passwords or traditional user profiles.
    """,
    version="2.0"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "https://paysure-frontend.vercel.app", # Placeholder
    "*" # Permissive for Hugging Face Spaces testing
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    # Structured Request Tracing
    logger.info(
        "request_trace",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        duration_ms=int(process_time * 1000)
    )
    return response

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

from fastapi import APIRouter
v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(projects.router)
v1_router.include_router(milestones.router)
v1_router.include_router(connections.router)
v1_router.include_router(transaction.router)
v1_router.include_router(disputes.router)
v1_router.include_router(wallet.router)
v1_router.include_router(admin.router)
v1_router.include_router(users.router)
v1_router.include_router(webhooks.router)

app.include_router(v1_router)

@app.get("/health", tags=["System"])
def health_check(db: Session = Depends(get_db)):
    """
    Application and Database Health Check.
    Returns 200 OK if the application is running and the database is accessible.
    """
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        return {"status": "degraded", "database": "disconnected"}
