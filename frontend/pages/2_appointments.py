import streamlit as st
import datetime
from api import get_patients, get_appointments, create_appointment, delete_appointment, update_appointment
# importing datetime to handle date objects
# importing from api.py so all HTTP requests stay in one place

st.title("Appointments")
st.caption("Manage patient appointments")
st.divider()

# ================================================================
# ADD APPOINTMENT FORM
# hidden behind an expander to keep the page clean
# ================================================================

with st.expander("Add New Appointment"):
    with st.form("add_appointment_form"):

        # fetch real patients from backend to populate the dropdown
        # this means the dropdown always reflects whoever is in the database
        # calls GET /patients via api.py
        patients = get_patients()

        # Format the label nicely and handle 'None' symptoms
        patient_options = {
            f"{p['name']} • {p['phone']}" + (f" ({p['symptoms']})" if p.get("symptoms") else ""): p["id"] 
            for p in patients
        }

        if not patient_options:
            # if no patients exist yet, warn the user
            # st.stop() halts rendering inside this block
            # nothing below it renders until patients are added
            st.warning("No patients found. Add patients first.")
            st.stop()

        col1, col2 = st.columns(2)

        # selectbox shows patient names from the dictionary keys
        patient_name = col1.selectbox("Patient", list(patient_options.keys()))
        doctor       = col2.text_input("Doctor Name", placeholder="")

        col3, col4 = st.columns(2)

        # date_input renders a calendar picker
        # defaults to today's date
        date = col3.date_input("Date", value=datetime.date.today())

        # fixed time slots as a dropdown
        # avoids freeform entry mistakes like "10am" vs "10:00 AM"
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
                # look up the patient id from the name the user selected
                # patient_options["Aisha Nair"] gives us 1
                response = create_appointment({
                    "patient_id": patient_options[patient_name],
                    "doctor": doctor,
                    # convert date object to string — backend expects "2025-05-15"
                    "date": str(date),
                    "time": time,
                    # always starts as Scheduled — user marks complete later
                    "status": "Scheduled",
                })
                if response.status_code == 200:
                    st.success(f"Appointment added for {patient_name}!")
                    st.rerun()
                else:
                    st.error("Something went wrong. Try again.")

# ================================================================
# FILTER BAR
# lets the user narrow appointments by status and date
# both filters are optional — defaults show everything
# ================================================================

st.subheader("All Appointments")

col1, col2 = st.columns(2)

# "All" means no status filter applied
status_filter = col1.selectbox("Filter by status", ["All", "Scheduled", "Completed"])

# value=None means the date picker starts empty — no filter by default
date_filter = col2.date_input("Filter by date", value=None)

# ================================================================
# FETCH APPOINTMENTS
# pass filters to the backend so filtering happens in the database
# not in python — more efficient, especially with large datasets
# ================================================================

appointments = get_appointments(
    # only pass date if user has selected one
    date=date_filter if date_filter else None,
    # only pass status if user picked something other than "All"
    status=status_filter if status_filter != "All" else None
)

if not appointments:
    st.info("No appointments found.")

else:
    # fetch patients to build a name lookup
    # appointments only store patient_id, not the name
    # so we need this to display "Aisha Nair" instead of "1"
    patients    = get_patients()

    # dictionary of id -> name
    # e.g. {1: "Aisha Nair", 2: "Rohan Das"}
    patient_map = {p["id"]: p["name"] for p in patients}

    for appt in appointments:
        with st.container(border=True):

            # 6 columns: patient, doctor, date, time, status, actions
            c1, c2, c3, c4, c5, c6 = st.columns([2, 2, 1, 1, 2, 2])

            # look up patient name using their id
            # .get() with "Unknown" default in case patient was deleted
            c1.write(f"**{patient_map.get(appt['patient_id'], 'Unknown')}**")
            c2.write(appt["doctor"])

            # date comes back as a string from the backend e.g. "2025-05-15"
            c3.write(appt["date"])
            c4.write(appt["time"])

            # colour coded status badge
            # same pattern as dashboard and patients page
            if appt["status"] == "Completed":
                c5.success("Completed")
            elif appt["status"] == "Scheduled":
                c5.info("Scheduled")
            else:
                c5.warning(appt["status"])

            # MARK AS COMPLETE BUTTON
            # only shows if appointment is not already completed
            # no point showing it when status is already Completed
            if appt["status"] != "Completed":
                if c6.button("Complete", key=f"complete_{appt['id']}"):
                    # calls PUT /appointments/{id} with just the status field
                    # exclude_unset in the backend means only status gets updated
                    response = update_appointment(appt["id"], {"status": "Completed"})
                    if response.status_code == 200:
                        st.success("Marked as completed.")
                        st.rerun()
                    else:
                        st.error("Could not update appointment.")

            # DELETE BUTTON
            # always visible regardless of status
            # unique key uses appointment id to avoid conflicts
            if c6.button("Delete", key=f"del_appt_{appt['id']}"):
                # calls DELETE /appointments/{id} via api.py
                response = delete_appointment(appt["id"])
                if response.status_code == 200:
                    st.success("Appointment deleted.")
                    st.rerun()
                else:
                    st.error("Could not delete appointment.")