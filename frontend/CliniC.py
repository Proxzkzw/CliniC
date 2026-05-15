import streamlit as st
import datetime
from api import get_patients, get_appointments
# importing api functions so dashboard shows real data from the database

st.set_page_config(page_title="CliniC", layout="wide")

# ================================================================
# REAL DATA FUNCTIONS
# these now call the actual backend instead of returning hardcoded data
# ================================================================

def get_stats():
    # fetch all patients and appointments from the backend
    patients     = get_patients()
    appointments = get_appointments()
    today = str(datetime.date.today())

    # count total patients — just the length of the list
    total_patients = len(patients)

    # filter appointments to only today's
    todays = [a for a in appointments if a["date"] == today]

    # count how many of today's are completed
    upcoming_count = len([
        a for a in appointments 
        if a['status'] == "Scheduled"
        and a['date']> today
    ])

    return {
        "total_patients":       total_patients,
        "todays_appointments":  len(todays),
        "upcoming_appointments":upcoming_count,
    }

def get_upcoming_appointments():
    # fetch all appointments then filter to scheduled ones from today onwards
    appointments = get_appointments()
    today        = str(datetime.date.today())

    # keep only scheduled appointments on or after today
    upcoming = [
        a for a in appointments
        if a["status"] == "Scheduled" and a["date"] >= today
    ]

    # sort by date so nearest appointments show first
    upcoming.sort(key=lambda a: a["date"])

    return upcoming

# ================================================================
# DASHBOARD
# ================================================================

st.title("🏥 CliniC")
st.caption(f"Today is {datetime.date.today().strftime('%A, %d %B %Y')}")
st.divider()

stats    = get_stats()
upcoming = get_upcoming_appointments()

col1, col2, col3 = st.columns(3)
col1.metric("Total Patients",        stats["total_patients"])
col2.metric("Today's Appointments",  stats["todays_appointments"])
col3.metric("Upcoming Appointments", stats["upcoming_appointments"])

st.divider()

st.subheader("Upcoming Appointments")

if not upcoming:
    st.info("No upcoming appointments.")
else:
    # fetch patient map so we can show names instead of ids
    patients    = get_patients()
    patient_map = {p["id"]: p["name"] for p in patients}

    for appt in upcoming:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([2, 2, 1, 1])

            # look up patient name from id
            c1.write(f"**{patient_map.get(appt['patient_id'], 'Unknown')}**")
            c2.write(appt["doctor"])
            c3.write(appt["date"])

            if appt["status"] == "Completed":
                c4.success("Completed")
            elif appt["status"] == "Scheduled":
                c4.info("Scheduled")
            else:
                c4.warning(appt["status"])