from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base

class ProjectStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    address = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with projects
    projects = relationship("Project", back_populates="customer")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)
    status = Column(String, default=ProjectStatus.PENDING.value)  # Store as string
    start_date = Column(Date, nullable=True)  # Changed to Date
    end_date = Column(Date, nullable=True)    # Changed to Date
    budget = Column(Float, nullable=True)
    revenue = Column(Float, nullable=True, default=0.0)  # Added revenue field
    customer_id = Column(Integer, ForeignKey("customers.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship with customer
    customer = relationship("Customer", back_populates="projects")
