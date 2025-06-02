import streamlit as st
from frontend.utils.api import api_get, api_post, api_delete
from frontend.utils.state import get_token

def activity_page():
    st.title("📝 Activity Log")
    token = get_token()
    res = api_get("/activity/log", token)
    logs = res.json() if res.ok else []
    st.write(logs)
    ticker = st.text_input("Log a Search (Ticker)")
    if st.button("Save Search"):
        r = api_post("/activity/save_search", token, params={"ticker": ticker})
        st.success(r.json().get("msg", "Search logged"))
    if st.button("Clear All Activity"):
        r = api_delete("/activity/clear", token)
        st.success(r.json().get("msg", "Activity log cleared"))
        st.rerun()
