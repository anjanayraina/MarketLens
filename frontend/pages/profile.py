import streamlit as st
from frontend.utils.api import api_get, api_put
from frontend.utils.state import get_token

def profile_page():
    st.title("👤 My Profile")
    token = get_token()
    res = api_get("/profile/me", token)
    profile = res.json() if res.ok else {}
    st.write("Profile:", profile)
    st.subheader("Update Profile")
    risk = st.selectbox("Risk Level", ["low", "medium", "high"], index=["low", "medium", "high"].index(profile.get("risk", "medium")))
    horizon = st.selectbox("Investment Horizon", ["1mo", "3mo", "6mo", "1y"], index=["1mo", "3mo", "6mo", "1y"].index(profile.get("horizon", "6mo")))
    if st.button("Save Profile"):
        r = api_put("/profile/update", token, json={"risk": risk, "horizon": horizon})
        st.success(r.json().get("msg", "Profile updated"))
        st.rerun()
