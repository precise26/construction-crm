from fastapi import FastAPI, Depends, HTTPException, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
from starlette.types import Scope, Receive, Send
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
import models, schemas, advanced_models
from database import engine, get_db, SessionLocal
import traceback
from datetime import datetime, timedelta
from pydantic import BaseModel
import logging
import json
from sqlalchemy import func
import os
from dotenv import load_dotenv
import uvicorn
from sqlalchemy import inspect

# Load environment variables from .env file
load_dotenv()

# Set up logging with more detailed format
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create database tables
models.Base.metadata.create_all(bind=engine)
advanced_models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Construction CRM")

print("Available routes:", [route.path for route in app.routes])

# Configure CORS
origins = [
    "https://www.grandterradevelopments.ca",
    "http://www.grandterradevelopments.ca",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://127.0.0.1:8000",
    "http://127.0.0.1:8080",
    "http://192.168.0.64:8000",
    "http://192.168.0.64:8080",
    "http://207.136.121.55:8000",
    "http://207.136.121.55:8080",
    "*"  # Allow all origins temporarily
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=3600,
)

class CORSStaticFiles(StaticFiles):
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            response = await super().__call__(scope, receive, send)
            if isinstance(response, FileResponse):
                response.headers.update({
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Methods": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Expose-Headers": "*",
                })
            return response
        await super().__call__(scope, receive, send)

def initialize_db(db: Session):
    # Check if tables are empty
    inspector = inspect(engine)
    
    # Initialize sample data only if customers table is empty
    if not db.query(models.Customer).first():
        print("Initializing sample data...")
        
        # Create sample customers
        customer1 = models.Customer(
            name="John Doe",
            email="john@example.com",
            phone="555-0101",
            address="123 Main St"
        )
        customer2 = models.Customer(
            name="Jane Smith",
            email="jane@example.com",
            phone="555-0102",
            address="456 Oak Ave"
        )
        db.add_all([customer1, customer2])
        db.commit()
        
        # Create sample projects
        project1 = models.Project(
            name="Kitchen Renovation",
            description="Full kitchen remodel",
            status="IN_PROGRESS",
            customer_id=1
        )
        project2 = models.Project(
            name="Bathroom Update",
            description="Master bathroom renovation",
            status="PLANNED",
            customer_id=2
        )
        db.add_all([project1, project2])
        db.commit()
        
        # Create sample leads
        lead1 = advanced_models.Lead(
            name="Bob Wilson",
            email="bob@example.com",
            phone="555-0103",
            address="789 Pine Rd",
            source="WEBSITE",
            status="NEW",
            notes="Interested in kitchen remodel"
        )
        db.add(lead1)
        db.commit()
        
        print("Sample data initialized successfully!")

@app.on_event("startup")
async def startup_event():
    db = SessionLocal()
    try:
        initialize_db(db)
    finally:
        db.close()

# Mount static files with CORS support
app.mount("/static", CORSStaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Customer endpoints
@app.post("/customers/", response_model=schemas.Customer)
def create_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    try:
        db_customer = models.Customer(**customer.model_dump())
        db.add(db_customer)
        db.commit()
        db.refresh(db_customer)
        return db_customer
    except Exception as e:
        db.rollback()
        print(f"Error creating customer: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customers/", response_model=List[schemas.Customer])
def list_customers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        customers = db.query(models.Customer).offset(skip).limit(limit).all()
        return customers
    except Exception as e:
        print(f"Error listing customers: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/customers/{customer_id}", response_model=schemas.CustomerWithProjects)
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        customer = db.query(models.Customer).options(
            joinedload(models.Customer.projects)
        ).filter(models.Customer.id == customer_id).first()
        
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        return customer
    except Exception as e:
        print(f"Error getting customer: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/customers/{customer_id}")
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    try:
        # Get the customer
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Get all projects for this customer
        projects = db.query(models.Project).filter(models.Project.customer_id == customer_id).all()
        project_ids = [project.id for project in projects]

        # Delete all related records in the correct order to avoid foreign key constraint errors
        
        # 1. Delete vendor projects first (they reference projects)
        if project_ids:
            db.query(advanced_models.VendorProject).filter(
                advanced_models.VendorProject.project_id.in_(project_ids)
            ).delete(synchronize_session=False)

        # 2. Delete notifications (they reference both customers and projects)
        db.query(advanced_models.Notification).filter(
            (advanced_models.Notification.customer_id == customer_id) |
            (advanced_models.Notification.project_id.in_(project_ids) if project_ids else False)
        ).delete(synchronize_session=False)

        # 3. Delete leads that reference this customer
        db.query(advanced_models.Lead).filter(
            advanced_models.Lead.converted_to_customer_id == customer_id
        ).delete(synchronize_session=False)

        # 4. Delete interactions
        db.query(advanced_models.Interaction).filter(
            advanced_models.Interaction.customer_id == customer_id
        ).delete(synchronize_session=False)

        # 5. Delete projects
        if project_ids:
            db.query(models.Project).filter(
                models.Project.id.in_(project_ids)
            ).delete(synchronize_session=False)

        # 6. Finally delete the customer
        db.query(models.Customer).filter(models.Customer.id == customer_id).delete(synchronize_session=False)

        db.commit()
        return {"message": f"Customer {customer_id} and all related records deleted successfully"}
    except Exception as e:
        db.rollback()
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Project endpoints
@app.post("/projects/", response_model=schemas.Project)
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    try:
        # Verify customer exists
        customer = db.query(models.Customer).filter(models.Customer.id == project.customer_id).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Convert the project data to dict
        project_data = project.model_dump()
        
        db_project = models.Project(**project_data)
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project
    except Exception as e:
        db.rollback()
        print(f"Error creating project: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/", response_model=List[schemas.Project])
def list_projects(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        projects = db.query(models.Project).options(
            joinedload(models.Project.customer)
        ).offset(skip).limit(limit).all()
        return projects
    except Exception as e:
        print(f"Error listing projects: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/projects/{project_id}", response_model=schemas.Project)
def get_project(project_id: int, db: Session = Depends(get_db)):
    try:
        project = db.query(models.Project).options(
            joinedload(models.Project.customer)
        ).filter(models.Project.id == project_id).first()
        
        if project is None:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return project
    except Exception as e:
        print(f"Error getting project: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"message": "Project deleted successfully"}

@app.get("/customers/{customer_id}/projects", response_model=List[schemas.Project])
def get_customer_projects(customer_id: int, db: Session = Depends(get_db)):
    try:
        customer = db.query(models.Customer).filter(models.Customer.id == customer_id).first()
        if customer is None:
            raise HTTPException(status_code=404, detail="Customer not found")
        return customer.projects
    except Exception as e:
        print(f"Error getting customer projects: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Vendor Endpoints
@app.post("/vendors/", response_model=schemas.Vendor)
def create_vendor(vendor: schemas.VendorCreate, db: Session = Depends(get_db)):
    try:
        db_vendor = advanced_models.Vendor(**vendor.model_dump())
        db.add(db_vendor)
        db.commit()
        db.refresh(db_vendor)
        return db_vendor
    except Exception as e:
        db.rollback()
        print(f"Error creating vendor: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vendors/", response_model=List[schemas.Vendor])
def list_vendors(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        vendors = db.query(advanced_models.Vendor).offset(skip).limit(limit).all()
        return vendors
    except Exception as e:
        print(f"Error listing vendors: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/vendors/{vendor_id}", response_model=schemas.Vendor)
def get_vendor(vendor_id: int, db: Session = Depends(get_db)):
    try:
        vendor = db.query(advanced_models.Vendor).filter(advanced_models.Vendor.id == vendor_id).first()
        if vendor is None:
            raise HTTPException(status_code=404, detail="Vendor not found")
        return vendor
    except Exception as e:
        print(f"Error getting vendor: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/vendors/{vendor_id}")
def delete_vendor(vendor_id: int, db: Session = Depends(get_db)):
    db_vendor = db.query(advanced_models.Vendor).filter(advanced_models.Vendor.id == vendor_id).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    db.delete(db_vendor)
    db.commit()
    return {"message": "Vendor deleted successfully"}

# Interaction Endpoints
@app.post("/interactions/", response_model=schemas.Interaction)
def create_interaction(interaction: schemas.InteractionCreate, db: Session = Depends(get_db)):
    try:
        db_interaction = advanced_models.Interaction(**interaction.model_dump())
        db.add(db_interaction)
        db.commit()
        db.refresh(db_interaction)
        return db_interaction
    except Exception as e:
        db.rollback()
        print(f"Error creating interaction: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/interactions/customer/{customer_id}", response_model=List[schemas.Interaction])
def get_customer_interactions(customer_id: int, db: Session = Depends(get_db)):
    try:
        interactions = db.query(advanced_models.Interaction).filter(
            advanced_models.Interaction.customer_id == customer_id
        ).all()
        return interactions
    except Exception as e:
        print(f"Error getting customer interactions: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Notification Endpoints
@app.post("/notifications/", response_model=schemas.Notification)
def create_notification(notification: schemas.NotificationCreate, db: Session = Depends(get_db)):
    try:
        db_notification = advanced_models.Notification(**notification.model_dump())
        db.add(db_notification)
        db.commit()
        db.refresh(db_notification)
        return db_notification
    except Exception as e:
        db.rollback()
        print(f"Error creating notification: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/notifications/", response_model=List[schemas.Notification])
def list_notifications(skip: int = 0, limit: int = 10, unread_only: bool = False, db: Session = Depends(get_db)):
    try:
        query = db.query(advanced_models.Notification)
        if unread_only:
            query = query.filter(advanced_models.Notification.is_read == False)
        notifications = query.offset(skip).limit(limit).all()
        return notifications
    except Exception as e:
        print(f"Error listing notifications: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

# Lead Endpoints
@app.post("/leads/", response_model=schemas.Lead)
def create_lead(lead: schemas.LeadCreate, db: Session = Depends(get_db)):
    try:
        # Log the incoming data
        logger.info("Incoming lead data: %s", json.dumps(lead.model_dump(), default=str))
        
        lead_data = lead.model_dump()
        
        # Status is already an enum from the schema validation
        db_lead = advanced_models.Lead(**lead_data)
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        logger.info("Lead created successfully with ID: %s", db_lead.id)
        return db_lead
    except Exception as e:
        db.rollback()
        logger.error("Error creating lead: %s", str(e))
        logger.error("Full traceback: %s", traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/leads/", response_model=List[schemas.Lead])
def list_leads(status: str = None, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    try:
        query = db.query(advanced_models.Lead)
        if status:
            query = query.filter(advanced_models.Lead.status == status)
        leads = query.offset(skip).limit(limit).all()
        return leads
    except Exception as e:
        print(f"Error listing leads: {str(e)}")
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/leads/{lead_id}", response_model=schemas.Lead)
def get_lead(lead_id: int, db: Session = Depends(get_db)):
    try:
        db_lead = db.query(advanced_models.Lead).filter(advanced_models.Lead.id == lead_id).first()
        if db_lead is None:
            raise HTTPException(status_code=404, detail="Lead not found")
        return db_lead
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/leads/{lead_id}")
async def delete_lead(lead_id: int, db: Session = Depends(get_db)):
    lead = db.query(advanced_models.Lead).filter(advanced_models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    
    try:
        db.delete(lead)
        db.commit()
        return {"message": "Lead deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

class LeadUpdate(BaseModel):
    status: str
    notes: Optional[str] = None
    next_follow_up: Optional[datetime] = None

@app.put("/leads/{lead_id}/status")
def update_lead_status(lead_id: int, lead_update: LeadUpdate, db: Session = Depends(get_db)):
    try:
        lead = db.query(advanced_models.Lead).filter(advanced_models.Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(status_code=404, detail="Lead not found")

        # Update lead status and fields
        lead.status = lead_update.status
        if lead_update.notes:
            lead.notes = lead_update.notes
        if lead_update.next_follow_up:
            lead.next_follow_up = lead_update.next_follow_up
        lead.last_contact = datetime.utcnow()

        db.commit()
        return {"message": "Lead status updated successfully"}
    except Exception as e:
        db.rollback()
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/leads/{lead_id}/convert", response_model=schemas.Customer)
async def convert_lead_to_customer(lead_id: int, db: Session = Depends(get_db)):
    # Get the lead
    lead = db.query(advanced_models.Lead).filter(advanced_models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Create new customer from lead data
    customer = models.Customer(
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        address=lead.address,
        is_active=True
    )
    db.add(customer)
    
    # Update lead status and conversion details
    lead.status = advanced_models.LeadStatus.CONVERTED
    lead.converted_at = datetime.utcnow()
    lead.converted_to_customer_id = customer.id
    
    try:
        db.commit()
        db.refresh(customer)
        return customer
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# Website Form Integration
class WebsiteFormData(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    message: Optional[str] = None
    project_type: Optional[str] = None
    address: Optional[str] = None
    source: Optional[str] = 'Website Contact Form'

@app.post("/api/website-form")
async def handle_website_form(
    form_data: WebsiteFormData,
    db: Session = Depends(get_db)
):
    try:
        # Create a new lead
        lead = advanced_models.Lead(
            name=form_data.name,
            email=form_data.email,
            phone=form_data.phone,
            address=form_data.address,
            description=form_data.message,
            project_type=form_data.project_type,
            source=form_data.source or 'Website Contact Form',
            status=advanced_models.LeadStatus.NEW,
            created_at=datetime.utcnow()
        )
        
        # Save lead to database
        db.add(lead)
        db.commit()
        db.refresh(lead)
        
        # Create a notification for the new lead
        notification = advanced_models.Notification(
            type=advanced_models.NotificationType.LEAD,
            title=f"New Lead from {form_data.source}: {form_data.name}",
            description=f"New contact form submission from {form_data.name} ({form_data.email})",
            due_date=datetime.utcnow() + timedelta(days=1)
        )
        db.add(notification)
        db.commit()

        return {
            "status": "success", 
            "message": "Form submitted successfully", 
            "lead_id": lead.id
        }
    
    except Exception as e:
        logger.error(f"Error processing website form: {str(e)}")
        logger.error(traceback.format_exc())
        db.rollback()
        raise HTTPException(status_code=500, detail="Error processing form submission")

# Admin endpoints
@app.post("/admin/clear-db")
def clear_database(db: Session = Depends(get_db)):
    try:
        # Clear all tables in the correct order to avoid foreign key constraints
        db.query(advanced_models.Interaction).delete()
        db.query(advanced_models.Notification).delete()
        db.query(advanced_models.VendorProject).delete()
        db.query(advanced_models.Vendor).delete()
        db.query(advanced_models.Lead).delete()
        db.query(models.Project).delete()
        db.query(models.Customer).delete()
        
        db.commit()
        return {"message": "Database cleared successfully"}
    except Exception as e:
        db.rollback()
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/dashboard/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    try:
        logger.info("Starting to fetch dashboard stats")
        
        # Get lead statistics
        logger.info("Fetching lead statistics")
        total_leads = db.query(advanced_models.Lead).count()
        logger.info(f"Total leads: {total_leads}")
        converted_leads = db.query(advanced_models.Lead).filter(advanced_models.Lead.status == "CONVERTED").count()
        logger.info(f"Converted leads: {converted_leads}")

        # Get customer statistics
        logger.info("Fetching customer statistics")
        total_customers = db.query(models.Customer).count()
        logger.info(f"Total customers: {total_customers}")
        active_customers = db.query(models.Customer).filter(models.Customer.is_active == True).count()
        logger.info(f"Active customers: {active_customers}")

        # Get project statistics
        logger.info("Fetching project statistics")
        total_projects = db.query(models.Project).count()
        logger.info(f"Total projects: {total_projects}")
        active_projects = db.query(models.Project).filter(
            models.Project.status == "in_progress"  
        ).count()
        logger.info(f"Active projects: {active_projects}")

        stats = {
            "leads": {
                "total": total_leads,
                "converted": converted_leads
            },
            "customers": {
                "total": total_customers,
                "active": active_customers
            },
            "projects": {
                "total": total_projects,
                "active": active_projects
            }
        }
        logger.info(f"Returning stats: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Error in get_dashboard_stats: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/debug")
async def debug_info():
    import socket
    local_ip = socket.gethostbyname(socket.gethostname())
    return {
        "local_ip": local_ip,
        "hostname": socket.gethostname(),
        "message": "Debug endpoint is working"
    }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=3000,
        reload=True,
        access_log=True,
        log_level="debug",
        proxy_headers=True,
        forwarded_allow_ips="*"
    )
