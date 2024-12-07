from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List
from advanced_models import InteractionType, NotificationType

# Vendor Schemas
class VendorBase(BaseModel):
    name: str
    contact_name: Optional[str] = None
    email: EmailStr
    phone: str
    address: Optional[str] = None
    specialty: Optional[str] = None

class VendorCreate(VendorBase):
    pass

class Vendor(VendorBase):
    id: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Interaction Schemas
class InteractionBase(BaseModel):
    customer_id: int
    project_id: Optional[int] = None
    interaction_type: InteractionType
    description: str
    notes: Optional[str] = None
    date: Optional[datetime] = None
    duration: Optional[float] = None

class InteractionCreate(InteractionBase):
    pass

class Interaction(InteractionBase):
    id: int

    class Config:
        from_attributes = True

# Notification Schemas
class NotificationBase(BaseModel):
    customer_id: Optional[int] = None
    project_id: Optional[int] = None
    type: NotificationType
    title: str
    description: Optional[str] = None
    is_read: bool = False
    due_date: Optional[datetime] = None

class NotificationCreate(NotificationBase):
    pass

class Notification(NotificationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# Lead Schemas
class LeadBase(BaseModel):
    name: str
    email: EmailStr
    phone: Optional[str] = None
    source: Optional[str] = None
    project_type: Optional[str] = None
    description: Optional[str] = None
    status: str = "new"

class LeadCreate(LeadBase):
    pass

class Lead(LeadBase):
    id: int
    created_at: datetime
    converted_at: Optional[datetime] = None
    converted_to_customer_id: Optional[int] = None

    class Config:
        from_attributes = True
