from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime

class Patient(Base):
    
    __tablename__ = "patients"

    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String, nullable=False)
    age        = Column(Integer)
    gender     = Column(String)
    phone      = Column(String)
    symptoms   = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)

    appointments = relationship("Appointment", back_populates="patient")


class Appointment(Base):
    __tablename__ = "appointments"

    id         = Column(Integer, primary_key=True, index=True)
    # stores patient id to link the two tables
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    doctor     = Column(String, nullable=False)
    date       = Column(Date, nullable=False)
    time       = Column(String, nullable=False)
    # defaults to Scheduled when a new appointment is created
    status     = Column(String, default="Scheduled")
    created_at = Column(DateTime, default=datetime.utcnow)

    # links back to the Patient model
    patient = relationship("Patient", back_populates="appointments")