import streamlit as st
import pandas as pd
from api import get_patients, create_patient, update_patient, delete_patient, get_appointments, delete_appointment

st.title("Patients")
st.divider()

# SEARCH BAR
# st.text_input returns whatever the user has typed
search = st.text_input("Search patient:", placeholder="Name")

# ================================================================
# ADD PATIENT FORM
# st.expander hides the form behind a toggle
# keeps the page clean — form only shows when user needs it
# ================================================================

with st.expander("Add New Patient"):

    # st.form groups all inputs together
    # streamlit only reruns when the submit button is clicked
    # without st.form it would rerun on every single keystroke
    with st.form("add_patient_form"):

        # split into two columns so fields sit side by side
        col1, col2 = st.columns(2)
        name      = col1.text_input("Name")

        # text_input instead of number_input to avoid the default zero
        # we manually validate and convert to int before sending to backend
        age_input = col2.text_input("Age", placeholder="")

        col3, col4 = st.columns(2)

        # selectbox gives a fixed dropdown — prevents invalid gender values
        gender   = col3.selectbox("Gender", ["Male", "Female", "Other"])
        phone    = col4.text_input("Phone Number")

        # text_area is multi-line — better for symptoms which can be long
        
        # form_submit_button triggers the rerun only when clicked
        # returns True when clicked, False otherwise
        submitted = st.form_submit_button("Add Patient")

        if submitted:
            # validate required fields before sending to backend
            # we check front end first to avoid unnecessary API calls
            if not name:
                st.error("Name is required.")
            elif not phone:
                st.error("Phone number is required.")
            elif not phone.isdigit():
                st.error("Phone no. can only contain numbers")
            elif len(phone)!=10:
                st.error("Phone no. should have 10 digits")
            elif not age_input:
                st.error("Age is required.")
            elif not age_input.isdigit():
                # isdigit() catches cases where someone types "abc"
                # prevents int() from crashing on invalid input
                st.error("Age must be a number.")
            else:
                # all fields valid — send to backend via api.py
                # create_patient() calls POST /patients
                response = create_patient({
                    "name": name,
                    "age": int(age_input),  # convert string to int here
                    "gender": gender,
                    "phone": phone,
                })
                if response.status_code == 200:
                    st.success(f"Patient {name} added successfully!")
                    # st.rerun() reruns the page so the table updates
                    # and shows the newly added patient immediately
                    st.rerun()
                else:
                    try:
                        error_msg = response.json().get("detail", f"Error: {response.text}")
                    except Exception as e:
                        error_msg = f"Failed to parse error: {e}. Response: {response.text}"
                    st.error(error_msg)

# ================================================================
# PATIENT TABLE
# fetches from the real backend via api.py
# if search is empty we pass None so all patients are returned
# if search has text we pass it and the backend filters the results
# ================================================================

st.subheader("All Patients")

patients = get_patients(search if search else None)

# always handle the empty state before trying to render the table
if not patients:
    st.info("No patients found.")

else:
    # loop through each patient returned by the backend
    for patient in patients:

        # border=True draws a subtle box around each patient card
        with st.container(border=True):

            # 5 columns: name+symptoms, age, gender, phone, action buttons
            # [3,1,1,2,2] means name col is wider, age and gender are narrow
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 2, 2])

            # ** makes text bold in streamlit markdown
            c1.write(f"**{patient['name']}**")

            # caption renders smaller muted text under the name
            # .get() used safely in case symptoms field is missing
            c1.caption(patient.get("symptoms", ""))

            c2.write(f"{patient['age']} yrs")
            c3.write(patient["gender"])
            c4.write(patient["phone"])

            # DELETE BUTTON
            # first click stores the patient id in session_state
            # this triggers the confirmation block below
            # actual deletion only happens after user confirms
            if c5.button("Delete", key=f"del_{patient['id']}"):
                st.session_state.delete_id = patient["id"]
                st.session_state.delete_name = patient["name"]

            # EDIT BUTTON
            # doesn't delete or save anything immediately
            # just stores the patient id in session_state
            # which triggers the edit form to appear below
            if c5.button("Edit", key=f"edit_{patient['id']}"):
                st.session_state.editing_id = patient["id"]

        # ================================================================
        # DELETE CONFIRMATION
        # renders outside the column block but still inside the for loop
        # so it appears under the correct patient card
        # session_state.delete_id tells us which patient is pending deletion
        # ================================================================

        if st.session_state.get("delete_id") == patient["id"]:

            # fetch all appointments and filter to this patient's
            all_appointments = get_appointments()
            patient_appointments = [
                a for a in all_appointments if a["patient_id"] == patient["id"]
            ]

            if patient_appointments:
                # patient has appointments — warn the user before deleting
                st.warning(
                    f"WARNING! **{patient['name']}** has **{len(patient_appointments)}** appointment(s). "
                    f"Deleting will also remove all their appointments. Are you sure?"
                )
                col_yes, col_no = st.columns(2)

                if col_yes.button("Yes, delete", key=f"confirm_del_{patient['id']}"):
                    # delete appointments first so foreign key constraint isn't violated
                    # then delete the patient
                    for appt in patient_appointments:
                        delete_appointment(appt["id"])
                    response = delete_patient(patient["id"])
                    if response.status_code == 200:
                        del st.session_state.delete_id
                        del st.session_state.delete_name
                        st.success("Patient and their appointments deleted.")
                        st.rerun()

                if col_no.button("Cancel", key=f"cancel_del_{patient['id']}"):
                    # user changed their mind — clear the pending delete
                    del st.session_state.delete_id
                    del st.session_state.delete_name
                    st.rerun()

            else:
                # no appointments — safe to delete straight away
                response = delete_patient(patient["id"])
                if response.status_code == 200:
                    del st.session_state.delete_id
                    del st.session_state.delete_name
                    st.success("Patient deleted.")
                    st.rerun()

# ================================================================
# EDIT FORM
# only renders when an edit button has been clicked
# we know which patient to edit from session_state.editing_id
# session_state survives reruns so the form stays visible
# ================================================================

if "editing_id" in st.session_state:

    # fetch fresh patient list from backend
    # then find the specific patient we want to edit
    all_patients = get_patients()
    patient_to_edit = next(
        # next() returns the first match from the generator
        # None is the default if no match is found
        (p for p in all_patients if p["id"] == st.session_state.editing_id), None
    )

    if patient_to_edit:
        st.divider()
        st.subheader(f"Editing: {patient_to_edit['name']}")

        with st.form("edit_patient_form"):
            col1, col2 = st.columns(2)

            # value= pre-fills each field with the patient's existing data
            name     = col1.text_input("Name", value=patient_to_edit["name"])

            # number_input is fine here since we already have a valid integer
            # from the database — no risk of the zero default problem
            age      = col2.number_input("Age", value=patient_to_edit["age"], min_value=0, max_value=200, step=1)

            col3, col4 = st.columns(2)

            gender   = col3.selectbox("Gender", ["Male", "Female", "Other"],
                           # index sets which option is pre-selected
                           # we find the position of the current gender in the list
                           # e.g. "Female" is at index 1
                           index=["Male", "Female", "Other"].index(patient_to_edit["gender"]))

            phone    = col4.text_input("Phone Number", value=patient_to_edit["phone"])


            col5, col6 = st.columns(2)
            save   = col5.form_submit_button("Save Changes")
            cancel = col6.form_submit_button("Cancel")

            if save:
                if not phone:
                    st.error("Phone number is required.")
                elif not phone.isdigit():
                    st.error("Phone no. can only contain numbers")
                elif len(phone) != 10:
                    st.error("Phone no. should have exactly 10 digits")
                else:
                    # calls PUT /patients/{id} with the updated fields
                    response = update_patient(st.session_state.editing_id, {
                        "name": name,
                        "age": age,
                        "gender": gender,
                        "phone": phone,
                    })
                if response.status_code == 200:
                    # remove editing_id from session_state
                    # this makes the edit form disappear
                    del st.session_state.editing_id
                    st.success("Patient updated successfully!")
                    st.rerun()
                else:
                    try:
                        error_msg = response.json().get("detail", f"Error: {response.text}")
                    except Exception as e:
                        error_msg = f"Failed to parse error: {e}. Response: {response.text}"
                    st.error(error_msg)

            if cancel:
                # discard changes — just clear the editing state
                # no API call needed since nothing was saved
                del st.session_state.editing_id
                st.rerun()

# ================================================================
# CSV EXPORT
# converts the patient list to a CSV file
# st.download_button lets the user download it directly from the browser
# ================================================================

st.divider()
st.subheader("Export Patients")

# fetch all patients from backend
patients_for_export = get_patients()

if not patients_for_export:
    st.info("No patients to export.")
else:
    # convert list of dictionaries to a pandas dataframe
    # each dictionary becomes a row, keys become column headers
    df = pd.DataFrame(patients_for_export)

    # convert dataframe to CSV string
    # index=False means don't include the row numbers in the export
    csv = df.to_csv(index=False)

    # st.download_button renders a button that triggers a file download
    # data      = the file contents
    # file_name = what the downloaded file will be called
    # mime      = file type, tells the browser this is a CSV
    st.download_button(
        label="⬇️ Download Patients CSV",
        data=csv,
        file_name="patients.csv",
        mime="text/csv",
    )