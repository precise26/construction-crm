from pydantic import BaseModel, EmailStr
from datetime import datetime, date
from typing import Optional, List
from models import ProjectStatus
from advanced_models import LeadStatus

class CustomerBase(BaseModel):
    name: str
    email: str
    phone: str
    address: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class VendorBase(BaseModel):
    name: str
    contact_name: Optional[str] = None
    email: str
    phone: str
    address: Optional[str] = None
    specialty: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int
    is_active: bool = True
    created_at: datetime = datetime.utcnow()

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str = ProjectStatus.PENDING.value  # Handle as string
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    customer_id: int

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime
    customer: Customer

    class Config:
        from_attributes = True

class CustomerWithProjects(Customer):
    projects: List[Project] = []

class InteractionBase(BaseModel):
    customer_id: int
    project_id: Optional[int] = None
    interaction_type: str
    description: str
    notes: Optional[str] = None
    date: datetime
    duration: Optional[float] = None

class InteractionCreate(InteractionBase):
    pass

class Interaction(InteractionBase):
    id: int
    customer: Customer
    project: Optional[Project] = None

    class Config:
        orm_mode = True

class LeadBase(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    address: Optional[str] = None
    source: Optional[str] = None
    project_type: Optional[str] = None
    description: Optional[str] = None
    status: LeadStatus = LeadStatus.NEW
    notes: Optional[str] = None
    next_follow_up: Optional[datetime] = None
    expected_value: Optional[float] = None

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    created_at: datetime
    converted_at: Optional[datetime] = None
    converted_to_customer_id: Optional[int] = None
    last_contact: Optional[datetime] = None

    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    customer_id: Optional[int] = None
    project_id: Optional[int] = None
    type: str
    title: str
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    is_read: bool = False

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    customer: Optional[Customer] = None
    project: Optional[Project] = None

    class Config:
        orm_mode = True
