import os
from dotenv import load_dotenv
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# 1. Load environment
def load_env():
    app_env = os.getenv("APP_ENV", "local").lower()
    env_file = "env.prod" if app_env == "prod" else "env.local"
    env_path = os.path.join("resources", env_file)
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded environment from {env_file}")
    else:
        print(f"Warning: {env_file} not found in resources/. Using defaults.")

load_env()
API_HOST = os.getenv("API_HOST", "http://localhost:8000")

# 2. Streamlit page config
st.set_page_config(page_title="Investor Insight", layout="wide")
st.sidebar.title("Investor Insight")

# 3. Session state for login/JWT
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None
if "username" not in st.session_state:
    st.session_state["username"] = None

# 4. Auth functions
def login(username, password):
    res = requests.post(f"{API_HOST}/auth/login", json={"username": username, "password": password})
    if res.status_code == 200:
        token = res.json()["access_token"]
        st.session_state["access_token"] = token
        st.session_state["username"] = username
        st.success("Logged in as " + username)
    else:
        st.error("Login failed. Check your username and password.")

def logout():
    st.session_state["access_token"] = None
    st.session_state["username"] = None

# 5. Sidebar: Login/Logout form
with st.sidebar.expander("Login", expanded=not st.session_state["access_token"]):
    if not st.session_state["access_token"]:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            login(username, password)
    else:
        st.write(f"Logged in as **{st.session_state['username']}**")
        if st.button("Logout"):
            logout()

# 6. Main app: Ticker and chart
st.title("📈 Stock Analysis Dashboard")
if st.session_state["access_token"]:
    ticker = st.text_input("Enter Stock Ticker (e.g., RELIANCE.NS)")
    horizon = st.selectbox("Select Time Horizon", [
        "1 Day", "5 Days", "1 Month", "3 Months", "6 Months", "1 Year", "5 Years", "Max"
    ])

    # Map UI horizon to API params
    HORIZON_CONFIG = {
        "1 Day":    {"period":"5d",  "interval":"5m"},
        "5 Days":   {"period":"5d",  "interval":"15m"},
        "1 Month":  {"period":"1mo", "interval":"1h"},
        "3 Months": {"period":"3mo", "interval":"1d"},
        "6 Months": {"period":"6mo", "interval":"1d"},
        "1 Year":   {"period":"1y",  "interval":"1d"},
        "5 Years":  {"period":"5y",  "interval":"1d"},
        "Max":      {"period":"max", "interval":"1wk"},
    }
    if ticker:
        cfg = HORIZON_CONFIG[horizon]
        headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
        # Fetch OHLC data
        res = requests.get(
            f"{API_HOST}/api/data/ohlc",
            params={"ticker": ticker, "period": cfg["period"], "interval": cfg["interval"]},
            headers=headers
        )
        if res.status_code == 200 and res.json():
            df = pd.DataFrame(res.json())
            if not df.empty:
                # Flexible column renaming (ensure API matches these names)
                col_map = {
                    "date": "date", "open": "open", "high": "high",
                    "low": "low", "close": "close"
                }
                df.rename(columns=col_map, inplace=True)
                if "date" in df.columns:
                    df["date"] = pd.to_datetime(df["date"])
                    st.subheader(f"Candlestick Chart: {ticker} ({horizon})")
                    fig = go.Figure(data=[go.Candlestick(
                        x=df["date"], open=df["open"], high=df["high"],
                        low=df["low"], close=df["close"]
                    )])
                    fig.update_layout(xaxis_rangeslider_visible=False)
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("Data format error: 'date' column not found.")
            else:
                st.warning("No OHLC data available for this ticker/horizon.")
        else:
            st.error("Error fetching OHLC data. Check ticker or backend connection.")

else:
    st.info("🔒 Please log in to view stock data.")

# (You can add more features here: saved stocks, AI advice, peers, etc.)
