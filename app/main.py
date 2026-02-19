from fastapi import FastAPI
from app.api import auth, users, projects
from app.api import transaction
from app.api import disputes


app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(transaction.router)
app.include_router(disputes.router)
