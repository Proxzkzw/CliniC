import requests
import os

BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")

def get_patients(search=None):
    params = {"search": search} if search else {}
    response = requests.get(f"{BASE_URL}/patients", params=params)
    return response.json()

def create_patient(data):
    response = requests.post(f"{BASE_URL}/patients", json=data)
    return response

def update_patient(patient_id, data):
    response = requests.put(f"{BASE_URL}/patients/{patient_id}", json=data)
    return response

def delete_patient(patient_id):
    response = requests.delete(f"{BASE_URL}/patients/{patient_id}")
    return response

def get_appointments(date=None, status=None):
    params = {}
    if date:
        params["date"] = str(date)
    if status and status != "All":
        params["status"] = status
    response = requests.get(f"{BASE_URL}/appointments", params=params)
    return response.json()

def create_appointment(data):
    response = requests.post(f"{BASE_URL}/appointments", json=data)
    return response

def delete_appointment(appointment_id):
    response = requests.delete(f"{BASE_URL}/appointments/{appointment_id}")
    return response

def update_appointment(appointment_id, data):
    response = requests.put(f"{BASE_URL}/appointments/{appointment_id}", json=data)
    return response