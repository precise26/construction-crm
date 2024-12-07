from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base
from models import Customer, Project

class InteractionType(enum.Enum):
    PHONE_CALL = "phone_call"
    EMAIL = "email"
    MEETING = "meeting"
    TEXT = "text"
    OTHER = "other"

class NotificationType(enum.Enum):
    FOLLOW_UP = "follow_up"
    PROJECT_MILESTONE = "project_milestone"
    TASK_REMINDER = "task_reminder"
    LEAD = "lead"
    COMPLETION = "completion"

class LeadStatus(enum.Enum):
    NEW = "NEW"
    PENDING = "PENDING"
    ACTIVE = "ACTIVE"
    QUALIFIED = "QUALIFIED"
    NEGOTIATING = "NEGOTIATING"
    CONVERTED = "CONVERTED"
    CLOSED = "CLOSED"
    LOST = "LOST"

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(String)
    specialty = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with projects
    projects = relationship("VendorProject", back_populates="vendor")

class VendorProject(Base):
    __tablename__ = "vendor_projects"

    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    project_id = Column(Integer, ForeignKey("projects.id"))
    role = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    status = Column(String)

    vendor = relationship("Vendor", back_populates="projects")
    project = relationship("Project")

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    interaction_type = Column(Enum(InteractionType))
    description = Column(Text)
    notes = Column(Text)
    date = Column(DateTime, default=datetime.utcnow)
    duration = Column(Float)  # in minutes
    
    customer = relationship("Customer")
    project = relationship("Project")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    type = Column(Enum(NotificationType))
    title = Column(String)
    description = Column(Text)
    is_read = Column(Boolean, default=False)
    due_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer")
    project = relationship("Project")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(String, nullable=True)
    source = Column(String)  # Website, Email, Referral, etc.
    project_type = Column(String)
    description = Column(Text, nullable=True)
    status = Column(Enum(LeadStatus), default=LeadStatus.NEW)
    created_at = Column(DateTime, default=datetime.utcnow)
    converted_at = Column(DateTime, nullable=True)
    converted_to_customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True)
    notes = Column(Text, nullable=True)
    last_contact = Column(DateTime, nullable=True)
    next_follow_up = Column(DateTime, nullable=True)
    expected_value = Column(Float, nullable=True)

    converted_customer = relationship("Customer")
