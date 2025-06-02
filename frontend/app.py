import os
import streamlit as st
import requests
from dotenv import load_dotenv


# --- ENV loading as before ---
def load_env():
    app_env = os.getenv("APP_ENV", "local").lower()
    env_file = "env.prod" if app_env == "prod" else "env.local"
    env_path = os.path.join("resources", env_file)
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)

load_env()
API_HOST = os.getenv("API_HOST", "http://localhost:8000")

# --- Auth/session state as before ---
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

headers = {}
if st.session_state["access_token"]:
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}

# --- Sidebar navigation ---
menu = st.sidebar.radio(
    "Navigation",
    ("Dashboard", "My Watchlist", "Profile", "Activity Log", "Logout" if st.session_state["access_token"] else "Login")
)

# --- Watchlist Page ---
if menu == "My Watchlist" and st.session_state["access_token"]:
    st.title("📈 My Saved Stocks")
    # List current watchlist
    res = requests.get(f"{API_HOST}/stocks/list", headers=headers)
    tickers = res.json() if res.ok else []
    st.write("Current watchlist:", tickers)

    # Add ticker
    new_ticker = st.text_input("Add Stock Ticker (e.g., RELIANCE.NS)")
    if st.button("Save Stock"):
        r = requests.post(f"{API_HOST}/stocks/save", params={"ticker": new_ticker}, headers=headers)
        st.success(r.json().get("msg", "Saved"))

    # Remove ticker
    ticker_to_remove = st.selectbox("Remove from Watchlist", tickers) if tickers else None
    if ticker_to_remove and st.button("Remove Stock"):
        r = requests.delete(f"{API_HOST}/stocks/remove", params={"ticker": ticker_to_remove}, headers=headers)
        st.success(r.json().get("msg", "Removed"))
        st.experimental_rerun()

# --- Profile Page ---
if menu == "Profile" and st.session_state["access_token"]:
    st.title("👤 My Profile")
    # View profile
    res = requests.get(f"{API_HOST}/profile/me", headers=headers)
    profile = res.json() if res.ok else {}
    st.write("Profile:", profile)

    # Update profile
    st.subheader("Update Profile")
    risk = st.selectbox("Risk Level", ["low", "medium", "high"], index=["low", "medium", "high"].index(profile.get("risk", "medium")))
    horizon = st.selectbox("Investment Horizon", ["1mo", "3mo", "6mo", "1y"], index=["1mo", "3mo", "6mo", "1y"].index(profile.get("horizon", "6mo")))
    if st.button("Save Profile"):
        r = requests.put(f"{API_HOST}/profile/update", json={"risk": risk, "horizon": horizon}, headers=headers)
        st.success(r.json().get("msg", "Profile updated"))
        st.experimental_rerun()

# --- Activity Log Page ---
if menu == "Activity Log" and st.session_state["access_token"]:
    st.title("📝 Activity Log")
    # List activity
    res = requests.get(f"{API_HOST}/activity/log", headers=headers)
    logs = res.json() if res.ok else []
    st.write(logs)

    # Log a search
    ticker = st.text_input("Log a Search (Ticker)")
    if st.button("Save Search"):
        r = requests.post(f"{API_HOST}/activity/save_search", params={"ticker": ticker}, headers=headers)
        st.success(r.json().get("msg", "Search logged"))

    # Clear activity
    if st.button("Clear All Activity"):
        r = requests.delete(f"{API_HOST}/activity/clear", headers=headers)
        st.success(r.json().get("msg", "Activity log cleared"))
        st.experimental_rerun()

# --- Auth/Login Page (very basic) ---
if (menu == "Login" or not st.session_state["access_token"]):
    st.title("🔐 Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        res = requests.post(f"{API_HOST}/auth/login", json={"username": username, "password": password})
        if res.ok:
            st.session_state["access_token"] = res.json()["access_token"]
            st.session_state["username"] = username
            st.success("Logged in!")
            st.experimental_rerun()
        else:
            st.error("Login failed.")

# --- Logout ---
if menu == "Logout" and st.session_state["access_token"]:
    if st.button("Confirm Logout"):
        st.session_state["access_token"] = None
        st.session_state["username"] = None
        st.experimental_rerun()
