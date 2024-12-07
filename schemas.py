from pydantic import BaseModel
from datetime import datetime, date
from typing import List, Optional
from models import ProjectStatus, LeadStatus, LeadSource

class CustomerBase(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    
    class Config:
        from_attributes = True

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True

class CustomerWithProjects(Customer):
    projects: List['Project'] = []
    
    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    name: str
    description: str
    status: ProjectStatus
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[float] = None
    customer_id: int
    
    class Config:
        from_attributes = True

class ProjectCreate(ProjectBase):
    pass

class Project(ProjectBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    customer: Customer
    
    class Config:
        from_attributes = True

class VendorBase(BaseModel):
    name: str
    contact_name: str
    email: str
    phone: str
    address: str
    specialty: str
    
    class Config:
        from_attributes = True

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int
    is_active: bool = True
    created_at: datetime = datetime.utcnow()
    updated_at: datetime | None = None
    
    class Config:
        from_attributes = True

class InteractionBase(BaseModel):
    customer_id: int
    project_id: Optional[int] = None
    interaction_type: str
    description: str
    notes: str
    date: datetime
    duration: Optional[float] = None
    
    class Config:
        from_attributes = True

class InteractionCreate(InteractionBase):
    pass

class Interaction(InteractionBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    customer: Customer
    project: Optional[Project] = None
    
    class Config:
        from_attributes = True

class NotificationBase(BaseModel):
    title: str
    description: str
    type: str
    customer_id: int | None = None
    project_id: int | None = None
    due_date: Optional[datetime] = None
    is_read: bool = False
    
    class Config:
        from_attributes = True

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    created_at: datetime
    read: bool = False
    customer: Optional[Customer] = None
    project: Optional[Project] = None
    
    class Config:
        from_attributes = True

class LeadBase(BaseModel):
    name: str
    email: str
    phone: str
    address: str
    source: LeadSource
    project_type: str
    description: str
    status: LeadStatus = LeadStatus.NEW
    notes: str | None = None
    next_follow_up: Optional[datetime] = None
    expected_value: Optional[float] = None
    
    class Config:
        from_attributes = True

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None
    converted_at: Optional[datetime] = None
    converted_to_customer_id: Optional[int] = None
    last_contact: Optional[datetime] = None
    
    class Config:
        from_attributes = True
