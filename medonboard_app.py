import streamlit as st
import mysql.connector
import pandas as pd
import hashlib


# Database connection
def create_connection():
    return mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="blue0025",
        database="medonboard"
    )


# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Check if username exists
def is_username_taken(username, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = %s", (username,))
    result = cursor.fetchone()
    return result[0] > 0


# Validate password
def is_valid_password(password, name, username):
    if len(password) < 8 or not any(char.isdigit() for char in password) or not any(
            char.isalpha() for char in password):
        return False
    if name in password or username in password:
        return False
    return True


# Initialize database
def init_db(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            role VARCHAR(100),
            user_type ENUM('normal', 'expert'),
            username VARCHAR(100) UNIQUE,
            password VARCHAR(255)
        )
    """)
    connection.commit()
    cursor.close()


# Add preset users
def add_preset_users(connection):
    cursor = connection.cursor()
    preset_users = [
        ('Expert User', 'Expert', 'expert', 'expert', hash_password('hello1234')),
        ('Normal User', 'User', 'normal', 'user', hash_password('hello1234'))
    ]
    for user in preset_users:
        cursor.execute(
            "INSERT IGNORE INTO users (name, role, user_type, username, password) VALUES (%s, %s, %s, %s, %s)", user)
    connection.commit()
    cursor.close()


# Authentication function
def authenticate_user(username, password, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT user_type FROM users WHERE username = %s AND password = %s",
                   (username, hash_password(password)))
    result = cursor.fetchone()
    cursor.close()
    if result:
        return result[0]
    return None


# Streamlit application
def main():
    st.set_page_config(page_title="MedonBoard", layout="centered", initial_sidebar_state="collapsed")
    connection = create_connection()
    init_db(connection)
    add_preset_users(connection)

    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False

    if not st.session_state.authenticated:
        st.markdown("# **MedonBoard**")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user_type = authenticate_user(username, password, connection)
            if user_type:
                st.session_state.authenticated = True
                st.session_state.user_type = user_type
                st.experimental_rerun()
            else:
                st.error("Invalid username or password")

        if st.button("Create Account"):
            create_account_page(connection)
    else:
        if st.session_state.user_type == 'normal':
            normal_user_homepage()
        elif st.session_state.user_type == 'expert':
            expert_user_homepage()


def create_account_page(connection):
    st.markdown("# **Create Account**")
    name = st.text_input("Name")
    role = st.text_input("Role")
    user_type = st.selectbox("User Type", ["normal", "expert"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    if st.button("Sign Up"):
        if password != confirm_password:
            st.error("Passwords do not match")
        elif is_username_taken(username, connection):
            st.error("Username already taken")
        elif not is_valid_password(password, name, username):
            st.error("Password does not meet criteria")
        else:
            cursor = connection.cursor()
            cursor.execute("INSERT INTO users (name, role, user_type, username, password) VALUES (%s, %s, %s, %s, %s)",
                           (name, role, user_type, username, hash_password(password)))
            connection.commit()
            cursor.close()
            st.success("Account created successfully")


def normal_user_homepage():
    st.markdown("# **Normal User Homepage**")
    st.markdown("Welcome to the MedonBoard!")
    navigation()


def expert_user_homepage():
    st.markdown("# **Expert User Homepage**")
    normal_user_homepage()
    st.markdown("### Edit Data")
    st.write("Functionality for expert users to edit data")


def navigation():
    # Set up the navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Medicines", "Diseases", "Case Records"])

    # Fetch data from database
    connection = create_connection()
    medicine_data = pd.read_sql("SELECT * FROM medicines", connection)
    disease_data = pd.read_sql("SELECT * FROM diseases", connection)
    case_record_data = pd.read_sql("SELECT * FROM case_records", connection)

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


if __name__ == "__main__":
    main()
