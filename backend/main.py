from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import engine, get_db

# creates all tables in the database if they don't exist yet
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="CliniC API")

# CORS allows your streamlit frontend to call this API
# without this the browser blocks the requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production you'd restrict this to your frontend url
    allow_methods=["*"],
    allow_headers=["*"],
)

# PATIENT ROUTES

@app.get("/patients", response_model=List[schemas.PatientResponse])
def get_patients(search: str = None, db: Session = Depends(get_db)):
    
    if search:
        # ilike is case insensitive LIKE — finds partial name matches
        return db.query(models.Patient).filter(
            models.Patient.name.ilike(f"%{search}%")
        ).all()
    return db.query(models.Patient).all()


@app.post("/patients", response_model=schemas.PatientResponse)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    # check for duplicate patient by phone number
    existing_patient = db.query(models.Patient).filter(models.Patient.phone == patient.phone).first()
    if existing_patient:
        raise HTTPException(status_code=400, detail="ERROR: another patient already exists with this phone number.")

    # convert pydantic schema to sqlalchemy model
    db_patient = models.Patient(**patient.model_dump())
    db.add(db_patient)
    db.commit()
    # refresh pulls the new id and created_at back from the database
    db.refresh(db_patient)
    return db_patient


@app.put("/patients/{patient_id}", response_model=schemas.PatientResponse)
def update_patient(patient_id: int, patient: schemas.PatientUpdate, db: Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
        
    if patient.phone:
        existing_patient = db.query(models.Patient).filter(
            models.Patient.phone == patient.phone, 
            models.Patient.id != patient_id
        ).first()
        if existing_patient:
            raise HTTPException(status_code=400, detail="ERROR: another patient already exists with this phone number.")

    # exclude_unset means only update fields the user actually sent
    # so if they only send name, age/gender/phone stay unchanged
    update_data = patient.model_dump(exclude_unset=True, exclude_none=True)
    
    for key, value in patient.model_dump(exclude_unset=True).items():
        setattr(db_patient, key, value)
    db.commit()
    db.refresh(db_patient)
    return db_patient


@app.delete("/patients/{patient_id}")
def delete_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not db_patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db.delete(db_patient)
    db.commit()
    return {"message": f"Patient {patient_id} deleted successfully"}

# APPOINTMENT ROUTES

@app.get("/appointments", response_model=List[schemas.AppointmentResponse])
def get_appointments(date: str = None, status: str = None, db: Session = Depends(get_db)):
    query = db.query(models.Appointment)
    if date:
        query = query.filter(models.Appointment.date == date)
    if status:
        query = query.filter(models.Appointment.status == status)
    return query.all()


@app.post("/appointments", response_model=schemas.AppointmentResponse)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    # check the patient actually exists before creating the appointment
    patient = db.query(models.Patient).filter(
        models.Patient.id == appointment.patient_id
    ).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    db_appointment = models.Appointment(**appointment.model_dump())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


@app.put("/appointments/{appointment_id}", response_model=schemas.AppointmentResponse)
def update_appointment(appointment_id: int, appointment: schemas.AppointmentUpdate, db: Session = Depends(get_db)):
    db_appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    
    update_date = appointment.model_dump(exclude_unset=True, exclude_none=True)
    for key, value in appointment.model_dump(exclude_unset=True).items():
        setattr(db_appointment, key, value)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment


@app.delete("/appointments/{appointment_id}")
def delete_appointment(appointment_id: int, db: Session = Depends(get_db)):
    db_appointment = db.query(models.Appointment).filter(
        models.Appointment.id == appointment_id
    ).first()
    if not db_appointment:
        raise HTTPException(status_code=404, detail="Appointment not found")
    db.delete(db_appointment)
    db.commit()
    return {"message": f"Appointment {appointment_id} deleted successfully"}