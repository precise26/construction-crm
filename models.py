from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Date, Text
from sqlalchemy.orm import relationship
from database import Base
import datetime
import enum

class ProjectStatus(enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class LeadStatus(enum.Enum):
    NEW = "NEW"
    CONTACTED = "CONTACTED"
    QUALIFIED = "QUALIFIED"
    PROPOSAL = "PROPOSAL"
    NEGOTIATION = "NEGOTIATION"
    WON = "WON"
    LOST = "LOST"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)
    address = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    # Relationships
    projects = relationship("Project", back_populates="customer", cascade="all, delete-orphan")
    interactions = relationship("Interaction", back_populates="customer", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="customer", cascade="all, delete-orphan")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    status = Column(String, nullable=False)
    start_date = Column(Date, nullable=True)  
    end_date = Column(Date, nullable=True)    
    budget = Column(Float, nullable=True)
    revenue = Column(Float, nullable=True, default=0.0)  
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="projects")
    interactions = relationship("Interaction", back_populates="project", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="project", cascade="all, delete-orphan")

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    contact_name = Column(String)
    email = Column(String, unique=True, nullable=False, index=True)
    phone = Column(String, nullable=False)
    services = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    interaction_type = Column(String, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)

    # Relationships
    customer = relationship("Customer", back_populates="interactions")
    project = relationship("Project", back_populates="interactions")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, nullable=False)
    customer_id = Column(Integer, ForeignKey("customers.id", ondelete="CASCADE"))
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    read = Column(Boolean, default=False, nullable=False)

    # Relationships
    customer = relationship("Customer", back_populates="notifications")
    project = relationship("Project", back_populates="notifications")

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False, index=True)
    phone = Column(String, nullable=False)
    address = Column(String)
    source = Column(String, nullable=False)
    status = Column(String, nullable=False)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, onupdate=datetime.datetime.utcnow)
