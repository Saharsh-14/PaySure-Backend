from sqlalchemy.orm import Session
from app.models.project import Project


# Create new project
def create_project(db: Session, title: str, description: str, client_id: str, freelancer_id: str):
    project = Project(
        title=title,
        description=description,
        client_id=client_id,
        freelancer_id=freelancer_id,
        status="active" # Assuming we start active if both are known
    )

    db.add(project)
    db.commit()
    db.refresh(project)

    return project


# Get project by ID
def get_project_by_id(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()


# Get all projects for a client
def get_projects_by_client(db: Session, client_id: str, skip: int = 0, limit: int = 100):
    return db.query(Project).filter(Project.client_id == client_id).offset(skip).limit(limit).all()


# Assign freelancer to project
def assign_freelancer(db: Session, project_id: int, freelancer_id: str):
    project = db.query(Project).filter(Project.id == project_id).first()

    if project:
        project.freelancer_id = freelancer_id
        project.status = "active"
        db.commit()
        db.refresh(project)

    return project
