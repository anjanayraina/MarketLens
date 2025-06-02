import streamlit as st
from frontend.utils.api import api_get, api_post, api_delete
from frontend.utils.state import get_token

def watchlist_page():
    st.title("📈 My Saved Stocks")
    token = get_token()
    res = api_get("/stocks/list", token)
    tickers = res.json() if res.ok else []
    st.write("Current watchlist:", tickers)
    new_ticker = st.text_input("Add Stock Ticker (e.g., RELIANCE.NS)")
    if st.button("Save Stock"):
        r = api_post("/stocks/save", token, params={"ticker": new_ticker})
        st.success(r.json().get("msg", "Saved"))
    ticker_to_remove = st.selectbox("Remove from Watchlist", tickers) if tickers else None
    if ticker_to_remove and st.button("Remove Stock"):
        r = api_delete("/stocks/remove", token, params={"ticker": ticker_to_remove})
        st.success(r.json().get("msg", "Removed"))
        st.rerun()
