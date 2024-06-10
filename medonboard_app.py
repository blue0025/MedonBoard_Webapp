import streamlit as st
import sqlite3
import pandas as pd
import hashlib


# Initialize SQLite database connection
def create_connection():
    conn = sqlite3.connect('medonboard.db')
    return conn


# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Check if username exists
def is_username_taken(username, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            role TEXT,
            user_type TEXT,
            username TEXT UNIQUE,
            password TEXT
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
        cursor.execute("INSERT OR IGNORE INTO users (name, role, user_type, username, password) VALUES (?, ?, ?, ?, ?)",
                       user)
    connection.commit()
    cursor.close()


# Authentication function
def authenticate_user(username, password, connection):
    cursor = connection.cursor()
    cursor.execute("SELECT user_type FROM users WHERE username = ? AND password = ?",
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

    st.markdown("# **MedonBoard**")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user_type = authenticate_user(username, password, connection)
        if user_type:
            if user_type == 'normal':
                normal_user_homepage()
            elif user_type == 'expert':
                expert_user_homepage()
        else:
            st.error("Invalid username or password")

    if st.button("Create Account"):
        create_account_page(connection)


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
            cursor.execute("INSERT INTO users (name, role, user_type, username, password) VALUES (?, ?, ?, ?, ?)",
                           (name, role, user_type, username, hash_password(password)))
            connection.commit()
            cursor.close()
            st.success("Account created successfully")


def normal_user_homepage():
    st.markdown("# **Normal User Homepage**")
    st.markdown("Welcome to the MedonBoard!")
    st.sidebar.markdown("## Categories")
    options = ["Medicine", "Diseases", "Case Records"]
    category = st.sidebar.selectbox("Select a category", options)
    if category == "Medicine":
        st.markdown("### Medicine")
        # Add Medicine page content
    elif category == "Diseases":
        st.markdown("### Diseases")
        # Add Diseases page content
    elif category == "Case Records":
        st.markdown("### Case Records")
        # Add Case Records page content
    st.sidebar.markdown("## Search")
    query = st.sidebar.text_input("Search for keywords")
    if st.sidebar.button("Search"):
        st.write(f"Search results for '{query}'")
        # Add search functionality


def expert_user_homepage():
    st.markdown("# **Expert User Homepage**")
    normal_user_homepage()
    st.markdown("### Edit Data")
    st.write("Functionality for expert users to edit data")
    # Add functionality to edit data


if __name__ == "__main__":
    main()
