from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.schemas.project import ProjectCreate, ProjectResponse
from app.crud.project import (
    create_project,
    get_project_by_id,
    get_projects_by_client,
    assign_freelancer
)
from app.api.deps import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


# ---------------------------
# CREATE PROJECT (Client Only)
# ---------------------------
@router.post("/", response_model=ProjectResponse)
def create_new_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can create projects")

    return create_project(
        db,
        title=project.title,
        description=project.description,
        client_id=current_user.id
    )


# ---------------------------
# GET MY PROJECTS
# ---------------------------
@router.get("/my", response_model=List[ProjectResponse])
def get_my_projects(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    return get_projects_by_client(db, current_user.id)


# ---------------------------
# ASSIGN FREELANCER
# ---------------------------
@router.put("/{project_id}/assign/{freelancer_id}", response_model=ProjectResponse)
def assign_project_freelancer(
    project_id: int,
    freelancer_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):

    if current_user.role != "client":
        raise HTTPException(status_code=403, detail="Only clients can assign freelancers")

    project = get_project_by_id(db, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return assign_freelancer(db, project_id, freelancer_id)
