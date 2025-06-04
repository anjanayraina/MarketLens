import streamlit as st
from frontend.utils.api import api_post
from frontend.utils.state import set_token

def login_page():
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        res = api_post("/auth/login", json={"username": username, "password": password})
        if res.ok:
            token = res.json()["access_token"]
            set_token(token)
            st.session_state["username"] = username
            st.success("Logged in!")
            st.rerun()
        else:
            st.error("Login failed.")
