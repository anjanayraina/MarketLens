import streamlit as st

def get_token():
    return st.session_state.get("access_token")

def set_token(token):
    st.session_state["access_token"] = token

def clear_token():
    st.session_state["access_token"] = None
    st.session_state["username"] = None
