from sqlalchemy.orm import Session
from database import engine
import models

# Create a new session
session = Session(bind=engine)

try:
    # Delete all records from each table in the correct order (to handle foreign key constraints)
    print("Clearing database entries...")
    
    # Clear projects first since they depend on customers
    print("Clearing projects...")
    session.query(models.Project).delete()
    
    # Then clear customers
    print("Clearing customers...")
    session.query(models.Customer).delete()
    
    # Commit the changes
    session.commit()
    print("Successfully cleared all entries from the database.")
except Exception as e:
    session.rollback()
    print(f"An error occurred: {e}")
finally:
    session.close()
