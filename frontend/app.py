import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Investor Insight", layout="wide")

API_HOST = st.secrets.get("API_HOST", "http://localhost:8000")

# Session state for login
if "access_token" not in st.session_state:
    st.session_state["access_token"] = None

def login(username, password):
    res = requests.post(f"{API_HOST}/auth/login", json={"username": username, "password": password})
    if res.status_code == 200:
        st.session_state["access_token"] = res.json()["access_token"]
        st.success("Logged in!")
    else:
        st.error("Login failed")

def get_ohlc(ticker, horizon):
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    res = requests.get(f"{API_HOST}/api/data/ohlc", params={"ticker": ticker, "horizon": horizon}, headers=headers)
    return res.json() if res.status_code == 200 else None

st.sidebar.title("Investor Insight")
with st.sidebar.expander("Login", expanded=True):
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        login(username, password)

st.title("Stock Analysis Dashboard")

if st.session_state["access_token"]:
    ticker = st.text_input("Enter Stock Ticker (e.g. RELIANCE.NS)")
    horizon = st.selectbox("Select Time Horizon", ["1d", "5d", "1mo", "6mo", "1y", "5y"])

    if ticker:
        st.subheader(f"OHLC Data for {ticker} - {horizon}")
        data = get_ohlc(ticker, horizon)
        if data:
            df = pd.DataFrame(data)
            fig = go.Figure(data=[go.Candlestick(x=df["date"],
                            open=df["open"], high=df["high"],
                            low=df["low"], close=df["close"])])
            fig.update_layout(xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data found or error fetching data.")
else:
    st.info("Please log in to view stock data.")
