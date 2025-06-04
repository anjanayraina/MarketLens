import os
import streamlit as st
from dotenv import load_dotenv
from utils.state import get_token, clear_token
from my_pages.chart import chart_page

def load_env():
    app_env = os.getenv("APP_ENV", "local").lower()
    env_file = "env.prod" if app_env == "prod" else "env.local"
    env_path = os.path.join("resources", env_file)
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)

load_env()

from my_pages.watchlist import watchlist_page
from my_pages.profile import profile_page
from my_pages.activity import activity_page
from my_pages.login import login_page
from my_pages.news import news_page
menu = st.sidebar.radio(
    "Navigation",
    ("Dashboard", "Chart", "My Watchlist", "Profile", "Activity Log" , "News", "Logout" if get_token() else "Login")
)

if menu == "Chart" and get_token():
    chart_page()
elif menu == "My Watchlist" and get_token():
    watchlist_page()
elif menu == "Profile" and get_token():
    profile_page()
elif menu == "Activity Log" and get_token():
    activity_page()
elif menu == "Login" or not get_token():
    login_page()
elif menu == "News" or not get_token():
    news_page()
elif menu == "Logout" and get_token():
    if st.button("Confirm Logout"):
        clear_token()
        st.rerun()
else:
    st.write("Welcome to Investor Insight!")
