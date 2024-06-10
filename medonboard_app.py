import streamlit as st
import pandas as pd

# Sample datasets for demonstration
medicine_data = pd.DataFrame({
    'name': ['Paracetamol', 'Ibuprofen', 'Amoxicillin'],
    'disease': ['Fever', 'Pain', 'Infection'],
    'usage': ['Relieves pain and reduces fever', 'Reduces inflammation and pain',
              'Antibiotic for bacterial infections'],
    'dose': ['500mg every 4-6 hours', '200mg every 4-6 hours', '500mg every 8 hours'],
    'disease_link': ['/diseases/fever', '/diseases/pain', '/diseases/infection']
})

disease_data = pd.DataFrame({
    'name': ['Fever', 'Pain', 'Infection'],
    'symptoms': ['High temperature', 'Discomfort and soreness', 'Bacterial growth'],
    'treatment': ['Paracetamol, rest, and hydration', 'Ibuprofen and rest', 'Antibiotics like Amoxicillin'],
    'medicine': ['Paracetamol', 'Ibuprofen', 'Amoxicillin'],
    'medicine_link': ['/medicines/paracetamol', '/medicines/ibuprofen', '/medicines/amoxicillin']
})

case_record_data = pd.DataFrame({
    'id': [1, 2, 3],
    'patient': ['John Doe', 'Jane Doe', 'Jim Beam'],
    'disease': ['Fever', 'Pain', 'Infection'],
    'medicine': ['Paracetamol', 'Ibuprofen', 'Amoxicillin'],
    'notes': ['Fever due to flu', 'Chronic back pain', 'Bacterial infection'],
    'disease_link': ['/diseases/fever', '/diseases/pain', '/diseases/infection']
})


# Authentication function
def authenticate(username, password, user_type):
    users = {
        'EXPERT': {'expert': 'hello1234'},
        'USER': {'user': 'hello1234'}
    }
    return users.get(user_type, {}).get(username) == password


# Check if user is authenticated
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center;'>MedonBoard</h1>", unsafe_allow_html=True)

    user_type = st.selectbox("Select User Type", ["EXPERT", "USER"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if authenticate(username, password, user_type):
            st.session_state.authenticated = True
            st.session_state.user_type = user_type
            st.experimental_rerun()
        else:
            st.error("Invalid username or password")

    if st.button("Create New User"):
        st.session_state.show_registration = True
        st.experimental_rerun()

elif 'show_registration' in st.session_state and st.session_state.show_registration:
    st.title("Create New User")

    new_username = st.text_input("New Username")
    new_email = st.text_input("Email")
    new_password = st.text_input("New Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")
    new_user_type = st.selectbox("Select User Type", ["EXPERT", "USER"])

    if st.button("Register"):
        if new_password != confirm_password:
            st.error("Passwords do not match")
        elif len(new_password) < 8 or not any(char.isdigit() for char in new_password) or not any(
                char.isalpha() for char in new_password):
            st.error("Password must be at least 8 characters long and include both numbers and alphabets")
        elif new_username in users[new_user_type]:
            st.error("Username already taken")
        else:
            users[new_user_type][new_username] = new_password
            st.success("User registered successfully")
            st.session_state.show_registration = False
            st.experimental_rerun()
else:
    # Set up the navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Medicines", "Diseases", "Case Records"])

    if page == "Medicines":
        st.title("Medicines")

        # Alphabet filter
        alphabet = st.selectbox("Filter by Alphabet", [chr(i) for i in range(ord('A'), ord('Z') + 1)])
        filtered_medicines = medicine_data[medicine_data['name'].str.startswith(alphabet)]

        # Search bar
        search_query = st.text_input("Search Medicines")
        if search_query:
            filtered_medicines = filtered_medicines[filtered_medicines['name'].str.contains(search_query, case=False)]

        # Display list of medicines
        for index, row in filtered_medicines.iterrows():
            if st.button(row['name']):
                st.write(f"**Name:** {row['name']}")
                st.write(f"**Disease:** [{row['disease']}]({row['disease_link']})")
                st.write(f"**Usage:** {row['usage']}")
                st.write(f"**Dose:** {row['dose']}")
    elif page == "Diseases":
        st.title("Diseases")

        # Alphabet filter
        alphabet = st.selectbox("Filter by Alphabet", [chr(i) for i in range(ord('A'), ord('Z') + 1)])
        filtered_diseases = disease_data[disease_data['name'].str.startswith(alphabet)]

        # Search bar
        search_query = st.text_input("Search Diseases")
        if search_query:
            filtered_diseases = filtered_diseases[filtered_diseases['name'].str.contains(search_query, case=False)]

        # Display list of diseases
        for index, row in filtered_diseases.iterrows():
            if st.button(row['name']):
                st.write(f"**Name:** {row['name']}")
                st.write(f"**Symptoms:** {row['symptoms']}")
                st.write(f"**Treatment:** {row['treatment']}")
                st.write(f"**Medicine:** [{row['medicine']}]({row['medicine_link']})")
    elif page == "Case Records":
        st.title("Case Records")

        # Search bar
        search_query = st.text_input("Search Case Records by Patient Name")
        filtered_cases = case_record_data
        if search_query:
            filtered_cases = filtered_cases[filtered_cases['patient'].str.contains(search_query, case=False)]

        # Display list of case records
        for index, row in filtered_cases.iterrows():
            if st.button(f"Case {row['id']} - {row['patient']}"):
                st.write(f"**Patient:** {row['patient']}")
                st.write(f"**Disease:** [{row['disease']}]({row['disease_link']})")
                st.write(f"**Medicine:** {row['medicine']}")
                st.write(f"**Notes:** {row['notes']}")

    # Logout button
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.experimental_rerun()
