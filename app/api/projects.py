from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.project import ProjectCreate, ProjectResponse
from app.services.project_service import (
    create_project_service,
    get_my_projects_service,
    assign_freelancer_service
)
from app.api.deps import get_current_user, RoleChecker

router = APIRouter(prefix="/projects", tags=["Projects"])


# ---------------------------
# CREATE PROJECT (Client Only)
# ---------------------------
@router.post("/", response_model=ProjectResponse)
def create_new_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["client"]))
):
    return create_project_service(db, project, current_user)


# ---------------------------
# GET MY PROJECTS
# ---------------------------
@router.get("/my", response_model=List[ProjectResponse])
def get_my_projects(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return get_my_projects_service(db, current_user, skip=skip, limit=limit)


# ---------------------------
# ASSIGN FREELANCER
# ---------------------------
@router.put("/{project_id}/assign/{freelancer_id}", response_model=ProjectResponse)
def assign_project_freelancer(
    project_id: int,
    freelancer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["client"]))
):
    return assign_freelancer_service(db, project_id, freelancer_id, current_user)
