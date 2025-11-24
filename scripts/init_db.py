#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and optionally seeds sample data
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import create_tables, SessionLocal
from database.models import User, CustomRule
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize the database"""
    print("Initializing database...")
    
    try:
        create_tables()
        print("✓ Database tables created successfully")
        
        # Optionally create a default user
        create_default_user()
        create_sample_rules()
        
        print("✓ Database initialization complete!")
        
    except Exception as e:
        print(f"✗ Error initializing database: {e}")
        import traceback
        traceback.print_exc()

def create_default_user():
    """Create a default user for testing"""
    db = SessionLocal()
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(
            User.email == "demo@codeaudit.com"
        ).first()
        
        if not existing_user:
            from passlib.context import CryptContext
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            
            demo_user = User(
                email="demo@codeaudit.com",
                hashed_password=pwd_context.hash("demo123"),
                full_name="Demo User",
                is_active=True
            )
            
            db.add(demo_user)
            db.commit()
            print("✓ Created demo user (email: demo@codeaudit.com, password: demo123)")
        else:
            print("  Demo user already exists")
    
    except Exception as e:
        print(f"  Warning: Could not create demo user: {e}")
    
    finally:
        db.close()

def create_sample_rules():
    """Create sample custom rules"""
    db = SessionLocal()
    
    try:
        # Check if rules exist
        existing_rules = db.query(CustomRule).count()
        
        if existing_rules == 0:
            sample_rules = [
                {
                    "user_id": "demo",
                    "name": "No print statements",
                    "description": "Discourage print statements in production code",
                    "rule_type": "forbidden",
                    "language": "python",
                    "pattern": "print\\(",
                    "severity": "warning",
                    "message": "Avoid using print() in production code. Use logging instead.",
                    "config": {"forbidden_items": ["print("]}
                },
                {
                    "user_id": "demo",
                    "name": "Function naming convention",
                    "description": "Functions should use snake_case",
                    "rule_type": "naming",
                    "language": "python",
                    "pattern": "^[a-z_][a-z0-9_]*$",
                    "severity": "info",
                    "message": "Function names should use snake_case",
                    "config": {}
                }
            ]
            
            for rule_data in sample_rules:
                rule = CustomRule(**rule_data)
                db.add(rule)
            
            db.commit()
            print(f"✓ Created {len(sample_rules)} sample custom rules")
        else:
            print("  Custom rules already exist")
    
    except Exception as e:
        print(f"  Warning: Could not create sample rules: {e}")
    
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
