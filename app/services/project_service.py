from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.crud.project import (
    create_project,
    get_project_by_id,
    get_projects_by_client,
    assign_freelancer
)
from app.schemas.project import ProjectCreate

def create_project_service(db: Session, project: ProjectCreate, current_user):
    """Business logic for creating a new project."""
    return create_project(
        db,
        title=project.title,
        description=project.description,
        client_id=current_user.id
    )

def get_my_projects_service(db: Session, current_user, skip: int = 0, limit: int = 100):
    """Business logic for retrieving user's projects."""
    return get_projects_by_client(db, current_user.id, skip=skip, limit=limit)

def assign_freelancer_service(db: Session, project_id: int, freelancer_id: int, current_user):
    """Business logic for assigning a freelancer to a project."""
    project = get_project_by_id(db, project_id)

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if project.client_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized")

    return assign_freelancer(db, project_id, freelancer_id)
