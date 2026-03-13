from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.models.connection import Connection, ConnectionStatus
from app.api.deps import CurrentUser
import uuid

def simulate_invite():
    db = SessionLocal()
    try:
        # Create a dummy client
        client_id = f"user_client_{uuid.uuid4().hex[:10]}"
        client = User(
            clerk_id=client_id,
            email=f"client_{uuid.uuid4().hex[:5]}@test.com",
            full_name="Test Client",
            role=UserRole.CLIENT
        )
        db.add(client)
        
        # Create a dummy freelancer
        freelancer_id = f"user_freelancer_{uuid.uuid4().hex[:10]}"
        freelancer = User(
            clerk_id=freelancer_id,
            email=f"freelancer_{uuid.uuid4().hex[:5]}@test.com",
            full_name="Test Freelancer",
            role=UserRole.FREELANCER
        )
        db.add(freelancer)
        db.commit()
        
        print(f"Created testing users: {client_id} (Client) and {freelancer_id} (Freelancer)")
        
        # Simulate invitation
        current_user = CurrentUser(clerk_id=client_id, email=client.email, role="Client")
        recipient_email = freelancer.email
        
        print(f"Simulating invite from {client_id} to {recipient_email}...")
        
        # Logic from connections.py
        recipient = db.query(User).filter(User.email == recipient_email).first()
        
        # Normalize roles
        recipient_role_str = recipient.role.value if hasattr(recipient.role, 'value') else str(recipient.role)
        current_role_str = str(current_user.role)
        
        if recipient_role_str.lower() == current_role_str.lower():
            print("Role mismatch error simulated")
            return

        # Check existing
        existing = db.query(Connection).filter(
            ((Connection.sender_id == current_user.clerk_id) & (Connection.recipient_id == recipient.clerk_id)) |
            ((Connection.sender_id == recipient.clerk_id) & (Connection.recipient_id == current_user.clerk_id))
        ).first()
        
        if existing:
            print("Existing connection found")
            return

        # Create
        c_id = current_user.clerk_id if current_role_str.lower() == "client" else recipient.clerk_id
        f_id = current_user.clerk_id if current_role_str.lower() == "freelancer" else recipient.clerk_id
        
        new_conn = Connection(
            sender_id=current_user.clerk_id,
            recipient_id=recipient.clerk_id,
            client_id=c_id,
            freelancer_id=f_id,
            status=ConnectionStatus.ACTIVE
        )
        
        db.add(new_conn)
        db.commit()
        print(f"SUCCESS: Connection created with id {new_conn.id}")
        
    except Exception as e:
        print(f"SIMULATION FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    simulate_invite()
