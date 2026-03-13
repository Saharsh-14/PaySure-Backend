import urllib.request
import urllib.parse
import json
import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User, UserRole
from app.core.config import settings

def bulk_sync():
    """
    Fetches all users from Clerk API and syncs them to the local database.
    Handles pagination for large user sets.
    """
    db = SessionLocal()
    try:
        # Determine Clerk API Base URL
        clerk_base = "https://api.clerk.com"
            
        print(f"Starting bulk sync from {clerk_base}...")
        
        limit = 100
        offset = 0
        total_processed = 0
        total_new = 0
        total_updated = 0
        
        while True:
            clerk_url = f"{clerk_base}/v1/users?limit={limit}&offset={offset}&sort=-created_at"
            req = urllib.request.Request(clerk_url)
            req.add_header("Authorization", f"Bearer {settings.CLERK_SECRET_KEY}")
            req.add_header("User-Agent", "curl/7.68.0")
            
            with urllib.request.urlopen(req) as response:
                users_data = json.loads(response.read().decode())
                
                if not users_data:
                    break
                
                for clerk_user in users_data:
                    clerk_id = clerk_user.get("id")
                    
                    # Get primary email
                    email = None
                    primary_email_id = clerk_user.get("primary_email_address_id")
                    email_addresses = clerk_user.get("email_addresses", [])
                    for email_obj in email_addresses:
                        if email_obj.get("id") == primary_email_id:
                            email = email_obj.get("email_address")
                            break
                    
                    if not email and email_addresses:
                        email = email_addresses[0].get("email_address")
                    
                    if not email:
                        continue
                        
                    email = email.lower()
                        
                    # Basic Info
                    first_name = clerk_user.get("first_name", "")
                    last_name = clerk_user.get("last_name", "")
                    full_name = f"{first_name} {last_name}".strip() or email.split('@')[0]
                    
                    # Role Discovery
                    public_metadata = clerk_user.get("public_metadata", {})
                    role_str = public_metadata.get("role")
                    
                    if not role_str:
                        unsafe_metadata = clerk_user.get("unsafe_metadata", {})
                        role_str = unsafe_metadata.get("role", "Client")
                    
                    # Map to Enum
                    try:
                        role = UserRole(role_str.capitalize() if role_str else "Client")
                    except ValueError:
                        role = UserRole.CLIENT
                    
                    # Check by clerk_id
                    user = db.query(User).filter(User.clerk_id == clerk_id).first()
                    
                    if not user:
                        # Check if email is already taken by ANOTHER clerk_id
                        user_by_email = db.query(User).filter(User.email == email).first()
                        if user_by_email:
                            print(f"Warning: Email {email} is already registered with clerk_id {user_by_email.clerk_id}. Updating that record to {clerk_id}...")
                            # Delete the old record and create new one to handle PK change, 
                            # or just update the old one if we want to preserve history.
                            # However, clerk_id is the primary key, so we should probably delete and recreate if the ID changed.
                            db.delete(user_by_email)
                            db.flush()
                        
                        user = User(clerk_id=clerk_id)
                        db.add(user)
                        total_new += 1
                    else:
                        total_updated += 1
                        
                    user.email = email
                    user.full_name = full_name
                    user.role = role
                    
                    total_processed += 1
                
                db.commit()
                print(f"Processed batch of {len(users_data)} users. (New: {total_new}, Updated: {total_updated})")
                
                if len(users_data) < limit:
                    break
                
                offset += limit
                
        print(f"Bulk sync completed. Total users processed: {total_processed}")
        
    except Exception as e:
        print(f"Error during bulk sync: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    bulk_sync()
