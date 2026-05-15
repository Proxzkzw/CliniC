# pyrefly: ignore [missing-import]
import streamlit as st

if "patients" not in st.session_state:
    st.session_state.patients = [
        {"id": 1, "name": "Aisha Nair",  "age": 28, "gender": "Female", "phone": "9876543210", "symptoms": "Fever, headache"},
        {"id": 2, "name": "Rohan Das",   "age": 35, "gender": "Male",   "phone": "9123456780", "symptoms": "Back pain"},
        {"id": 3, "name": "Leela Iyer",  "age": 52, "gender": "Female", "phone": "9012345678", "symptoms": "Diabetes checkup"},
    ]
# using mockdata so referring to local hardcoded data, will switch
def get_patients():
    return st.session_state.patients

def search_patient(name):
    return [p for p in st.session_state.patients if name.lower() in p["name"].lower()]

def add_patient(data):
    new_id = max(p["id"] for p in st.session_state.patients)+1
    st.session_state.patients.append({"id": new_id, **data})

def delete_patient(patient_id):
    st.session_state.patients = [p for p in st.session_state.patients if p["id"] != patient_id]
def update_patient(patient_id,data):
    for p in st.session_state.patients:
        if p["id"] == patient_id:
            p.update(data)
            break


st.title("Patients")
st.divider()

#srchbar
search= st.text_input("Search patient:",placeholder= "Name")

#toggle
with st.expander("Add New Patient"):

     with st.form("add_patient_form"):

        
        col1, col2 = st.columns(2)
        name   = col1.text_input("Name")
        age    = col2.number_input("Age", min_value=0, max_value=120, step=1)

        col3, col4 = st.columns(2)
       #dropdown
        gender = col3.selectbox("Gender", ["Male", "Female", "Other"])
        phone  = col4.text_input("Phone Number")

       
        symptoms = st.text_area("Symptoms", placeholder=" ")

        
        submitted = st.form_submit_button("Add Patient")

        if submitted:
            
            if not name:
                st.error("Name is required.")
            elif not phone:
                st.error("Phone number is required.")
            else:
                add_patient({
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "phone": phone,
                    "symptoms": symptoms,
                })
                
                st.success(f"Patient {name} added successfully!")
                
                st.rerun()

st.subheader("All Patients")

if search:
    patients = search_patient(search)
else:
    patients = get_patients()

if not patients:
    st.info("No patients found.")

else:
    for patient in patients:
        with st.container(border=True):

            #action buttons for name, age, gender, phone, X
            c1, c2, c3, c4, c5 = st.columns([3, 1, 1, 2, 2])

            c1.write(f"**{patient['name']}**")
            c1.caption(patient["symptoms"])  
            c2.write(f"{patient['age']} yrs")
            c3.write(patient["gender"])
            c4.write(patient["phone"])

            #patient id  used to make delete key for each patient
            if c5.button("Delete", key=f"del_{patient['id']}"):
                delete_patient(patient["id"])
                st.success("Patient deleted.")
                st.rerun()

            
            if c5.button("Edit", key=f"edit_{patient['id']}"):
                st.session_state.editing_id = patient["id"]


# EDIT FORM

# check if currently editing patient
if "editing_id" in st.session_state:

    # used to find patient id from stored 
    patient_to_edit = next(
        (p for p in st.session_state.patients if p["id"] == st.session_state.editing_id),
        None 
    )

    if patient_to_edit:
        st.divider()
        st.subheader(f"Editing: {patient_to_edit['name']}")

        with st.form("edit_patient_form"):
            col1, col2 = st.columns(2)

            # value= pre-fills  input with existing data
            name     = col1.text_input("Name",   value=patient_to_edit["name"])
            age = col2.number_input("Age", min_value=0, max_value=120, step=1, value=None, placeholder=" ")

            col3, col4 = st.columns(2)
            gender   = col3.selectbox("Gender", ["Male", "Female", "Other"],
                           index=["Male", "Female", "Other"].index(patient_to_edit["gender"]))
            phone    = col4.text_input("Phone Number", value=patient_to_edit["phone"])
            symptoms = st.text_area("Symptoms", value=patient_to_edit("symptoms",""))

            col5, col6 = st.columns(2)
            save      = col5.form_submit_button("Save Changes")
            cancel    = col6.form_submit_button("Cancel")

            if save:
                update_patient(st.session_state.editing_id, {
                    "name": name,
                    "age": age,
                    "gender": gender,
                    "phone": phone,
                    "symptoms": symptoms,
                })
                # clear editing state so form disappears
                del st.session_state.editing_id
                st.success("Patient updated successfully!")
                st.rerun()

            if cancel:
                #clear the editing state without saving
                del st.session_state.editing_id
                st.rerun()