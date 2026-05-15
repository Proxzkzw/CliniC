import streamlit as st
import datetime

# ================================================================
# MOCK DATA
# same pattern as patients — session_state keeps data alive between reruns
# appointments are linked to patients via patient_name
# when backend is ready replace these functions with requests calls
# ================================================================

if "appointments" not in st.session_state:
    st.session_state.appointments = [
        {"id": 1, "patient": "Aisha Nair",  "doctor": "Dr. Mehta", "date": datetime.date(2025, 5, 15), "time": "10:00 AM", "status": "Scheduled"},
        {"id": 2, "patient": "Rohan Das",   "doctor": "Dr. Priya", "date": datetime.date(2025, 5, 15), "time": "11:30 AM", "status": "Scheduled"},
        {"id": 3, "patient": "Leela Iyer",  "doctor": "Dr. Mehta", "date": datetime.date(2025, 5, 16), "time": "02:00 PM", "status": "Completed"},
    ]
#helper functinos


def get_appointments():
    
    return st.session_state.appointments

def add_appointment(data):
    new_id = max(a["id"] for a in st.session_state.appointments) + 1
    st.session_state.appointments.append({"id": new_id, **data})

def delete_appointment(appointment_id):
    st.session_state.appointments = [
        a for a in st.session_state.appointments if a["id"] != appointment_id
    ]

def update_status(appointment_id, new_status):
    for a in st.session_state.appointments:
        if a["id"] == appointment_id:
            a["status"] = new_status
            break



st.title("Appointments")
st.divider()

# ADD APPOINTMENT FORM

with st.expander("Add New Appointment"):
    with st.form("add_appointment_form"):

        #patient names pulledfrom session_statea
        patient_names = [p["name"] for p in st.session_state.get("patients", [])]

        if not patient_names:
            
            st.warning("No patients found. Add patients first from the Patients page.")
            st.stop()

        col1, col2 = st.columns(2)

        patient = col1.selectbox("Patient", patient_names)
        doctor  = col2.text_input("Doctor Name", placeholder=" ")

        col3, col4 = st.columns(2)

        date = col3.date_input("Date", value=datetime.date.today())

        time = col4.selectbox("Time", [
            "09:00 AM", "09:30 AM", "10:00 AM", "10:30 AM",
            "11:00 AM", "11:30 AM", "12:00 PM", "12:30 PM",
            "02:00 PM", "02:30 PM", "03:00 PM", "03:30 PM",
            "04:00 PM", "04:30 PM", "05:00 PM",
        ])

        submitted = st.form_submit_button("Add Appointment")

        if submitted:
            if not doctor:
                st.error("Doctor name is required.")
            else:
                add_appointment({
                    "patient": patient,
                    "doctor": doctor,
                    "date": date,
                    "time": time,
                    "status": "Scheduled",
                })
                st.success(f"Appointment scheduled for {patient}!")
                st.rerun()


# FILTER BAR for users

st.subheader("All Appointments")

col1, col2 = st.columns(2)

status_filter = col1.selectbox("Filter by status", ["All", "Scheduled", "Completed"])


date_filter = col2.date_input("Filter by date", value=None)


# APPLY FILTERS

appointments = get_appointments()

if status_filter != "All":
    appointments = [a for a in appointments if a["status"] == status_filter]

if date_filter:
    
    appointments = [a for a in appointments if a["date"] == date_filter]


# APPOINTMENT TABLE

if not appointments:
    st.info("No appointments found.")

else:
    for appt in appointments:
        with st.container(border=True):

            # patient, doctor, date, time, status, actions
            c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 1, 1, 1, 2])

            c1.write(f"**{appt['patient']}**")
            c2.write(appt["doctor"])

            c3.write(appt["date"].strftime("%d %b %Y"))
            c4.write(appt["time"])

            if appt["status"] == "Completed":
                c5.success("Completed")
            elif appt["status"] == "Scheduled":
                c5.info("Scheduled")
            else:
                c5.warning(appt["status"])

            if appt["status"] != "Completed":
                if c6.button("✅ Complete", key=f"complete_{appt['id']}"):
                    update_status(appt["id"], "Completed")
                    st.success("Appointment marked as completed.")
                    st.rerun()

            if c6.button("🗑 Delete", key=f"del_appt_{appt['id']}"):
                delete_appointment(appt["id"])
                st.success("Appointment deleted.")
                st.rerun()
