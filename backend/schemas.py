from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional

# PATIENT SCHEMAS
#seprt schemas used for innput adn output

class PatientCreate(BaseModel):
    #fields the frontend sends when creating a patient
    name: str
    age: int
    gender: str
    phone: str
    symptoms: Optional[str] = None 

class PatientUpdate(BaseModel):
    # all fields optional for updates 
    name:     Optional[str] = None
    age:      Optional[int] = None
    gender:   Optional[str] = None
    phone:    Optional[str] = None
    symptoms: Optional[str] = None

class PatientResponse(BaseModel):
    # data sent back 
    id:         int
    name:       str
    age:        int
    gender:     str
    phone:      str
    symptoms:   Optional[str] = None
    created_at: datetime

    class Config:
        # allows pydantic to read sqlalchemy objects directly
        # without this pydantic can't convert your db rows to json
        from_attributes = True

# APPOINTMENT SCHEMAS

class AppointmentCreate(BaseModel):
    patient_id: int
    doctor:     str
    date:       date
    time:       str
    status:     Optional[str] = "Scheduled"

class AppointmentUpdate(BaseModel):
    doctor: Optional[str] = None
    date:   Optional[date] = None
    time:   Optional[str]  = None
    status: Optional[str]  = None

class AppointmentResponse(BaseModel):
    id:         int
    patient_id: int
    doctor:     str
    date:       date
    time:       str
    status:     str
    created_at: datetime

    class Config:
        from_attributes = True