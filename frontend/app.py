import os
from dotenv import load_dotenv
import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# --- CONFIGURATION & ENVIRONMENT LOADING ---

HORIZON_CONFIG = {
    "1 Day":    {"period": "5d",  "interval": "5m"},
    "5 Days":   {"period": "5d",  "interval": "15m"},
    "1 Month":  {"period": "1mo", "interval": "1h"},
    "3 Months": {"period": "3mo", "interval": "1d"},
    "6 Months": {"period": "6mo", "interval": "1d"},
    "1 Year":   {"period": "1y",  "interval": "1d"},
    "5 Years":  {"period": "5y",  "interval": "1d"},
    "Max":      {"period": "max", "interval": "1wk"},
}

def load_env():
    """Load environment variables from resources/env.local or env.prod."""
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

# --- SESSION STATE INITIALIZATION ---

def init_session():
    st.session_state.setdefault("access_token", None)
    st.session_state.setdefault("username", None)

init_session()

# --- AUTHENTICATION ---

def login(username, password):
    """Authenticate user and store JWT token in session state."""
    try:
        res = requests.post(f"{API_HOST}/auth/login", json={
            "username": username, "password": password
        })
        if res.status_code == 200:
            token = res.json().get("access_token")
            st.session_state["access_token"] = token
            st.session_state["username"] = username
            st.success(f"Logged in as {username}")
        else:
            st.error("Login failed. Check your username and password.")
    except Exception as e:
        st.error(f"Login error: {e}")

def logout():
    """Clear login info from session state."""
    st.session_state["access_token"] = None
    st.session_state["username"] = None

def render_login_sidebar():
    """Sidebar login/logout form."""
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

# --- DATA FETCHING & VISUALIZATION ---

def fetch_ohlc(ticker, period, interval, token):
    """Fetch OHLC data from the backend."""
    headers = {"Authorization": f"Bearer {token}"}
    try:
        res = requests.get(
            f"{API_HOST}/api/data/ohlc",
            params={"ticker": ticker, "period": period, "interval": interval},
            headers=headers
        )
        if res.status_code == 200 and res.json():
            return pd.DataFrame(res.json())
        return None
    except Exception as e:
        st.error(f"Error fetching OHLC: {e}")
        return None

def render_candlestick_chart(df, ticker, horizon):
    """Render a Plotly candlestick chart."""
    required_cols = {"date", "open", "high", "low", "close"}
    if not required_cols.issubset(df.columns):
        st.warning("Data format error: required columns missing.")
        return
    df["date"] = pd.to_datetime(df["date"])
    st.subheader(f"Candlestick Chart: {ticker} ({horizon})")
    fig = go.Figure(
        data=[
            go.Candlestick(
                x=df["date"],
                open=df["open"], high=df["high"],
                low=df["low"], close=df["close"]
            )
        ]
    )
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

def main_dashboard():
    """Main stock dashboard: ticker input and chart display."""
    st.title("📈 Stock Analysis Dashboard")
    if not st.session_state["access_token"]:
        st.info("🔒 Please log in to view stock data.")
        return

    ticker = st.text_input("Enter Stock Ticker (e.g., RELIANCE.NS)")
    horizon = st.selectbox("Select Time Horizon", list(HORIZON_CONFIG.keys()))

    if ticker:
        cfg = HORIZON_CONFIG[horizon]
        df = fetch_ohlc(ticker, cfg["period"], cfg["interval"], st.session_state["access_token"])
        if df is not None and not df.empty:
            col_map = {
                "date": "date", "open": "open", "high": "high",
                "low": "low", "close": "close"
            }
            df.rename(columns=col_map, inplace=True)
            render_candlestick_chart(df, ticker, horizon)
        elif df is not None:
            st.warning("No OHLC data available for this ticker/horizon.")
        # If df is None, error already handled in fetch_ohlc

# --- STREAMLIT PAGE CONFIG & RENDER ---

st.set_page_config(page_title="Investor Insight", layout="wide")
st.sidebar.title("Investor Insight")

render_login_sidebar()
main_dashboard()

# (Add more feature functions below: saved stocks, advice, sentiment, etc.)
