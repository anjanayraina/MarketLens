import os
import streamlit as st
from dotenv import load_dotenv
from utils.state import get_token, clear_token

def load_env():
    app_env = os.getenv("APP_ENV", "local").lower()
    env_file = "env.prod" if app_env == "prod" else "env.local"
    env_path = os.path.join("resources", env_file)
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)

load_env()

from pages.watchlist import watchlist_page
from pages.profile import profile_page
from pages.activity import activity_page
from pages.login import login_page

menu = st.sidebar.radio(
    "Navigation",
    ("Dashboard", "My Watchlist", "Profile", "Activity Log", "Logout" if get_token() else "Login")
)

if menu == "My Watchlist" and get_token():
    watchlist_page()
elif menu == "Profile" and get_token():
    profile_page()
elif menu == "Activity Log" and get_token():
    activity_page()
elif menu == "Login" or not get_token():
    login_page()
elif menu == "Logout" and get_token():
    if st.button("Confirm Logout"):
        clear_token()
        st.rerun()
else:
    st.write("Welcome to Investor Insight!")
