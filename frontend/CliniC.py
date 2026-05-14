import genericpath
import streamlit as st
import datetime

st.set_page_config(page_title="CliniC", layout="wide")
## AI
# ================================================================
# MOCK DATA FUNCTIONS
# these return hardcoded data for now
# when your backend is ready, you'll replace the return value with:
# import requests
# return requests.get("http://localhost:8000/...").json()
# ================================================================


# will later call GET /patients and GET /appointments from  FastAPI backend
    
def get_stats():
    return {
        "total_patients": 24,
        "todays_appointments": 5,
        "completed_today": 3,
    }

def get_upcoming_appointments():
    
    return [
        {"patient": "Aisha Nair", "doctor": "Dr. Mehta", "time": "10:00 AM", "status": "Scheduled"},
        {"patient": "Rohan Das",  "doctor": "Dr. Priya", "time": "11:30 AM", "status": "Scheduled"},
        {"patient": "Leela Iyer", "doctor": "Dr. Mehta", "time": "02:00 PM", "status": "Completed"},
    ]

st.title("Clinic Dashboard")

st.divider()

#metrics

stats = get_stats()

col1,col2,col3 = st.columns(3)
# puts metrics into cards
col1.metric("Total Patients", stats["total_patients"])
col2.metric("Today's Appointments", stats["todays_appointments"])
col3.metric("Completed Today", stats["completed_today"])

#for upcoming appointments

st.divider()
st.subheader("Upcoming Appointments")

upcoming = get_upcoming_appointments()

if not upcoming:
    st.info("No upcoming appointments")

else:
    for appt in upcoming:

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])

            c1.write(f"**Patient:**{appt['patient']}")
            c2.write(appt["doctor"])
            c3.write(appt["time"])
            
            #color coded statuses
            if appt["status"] == "Completed":
                c4.success("Completed")
            elif appt["status"] == "Scheduled":
                c4.info("Scheduled")
            else:
                c4.warning(appt["status"])



