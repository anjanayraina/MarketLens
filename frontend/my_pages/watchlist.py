import streamlit as st
from frontend.utils.api import api_get, api_post, api_delete
from frontend.utils.state import get_token

def watchlist_page():
    st.title("📈 My Saved Stocks")
    st.caption("Manage your personalized stock watchlist below.")

    token = get_token()

    # Get current watchlist
    res = api_get("/stocks/list", token)
    tickers = res.json() if res.ok else []

    st.markdown("#### Your Watchlist")
    if not tickers:
        st.info("No stocks saved yet. Add your favorites! ⭐")
    else:
        cols = st.columns(min(4, len(tickers)))
        for idx, ticker in enumerate(tickers):
            with cols[idx % len(cols)]:
                st.markdown(
                    f"""
                    <div style='background:#f0f2f6;padding:1.2em 1em;border-radius:16px;
                    box-shadow:0 2px 8px rgba(0,0,0,0.07);margin-bottom:1em;'>
                        <span style='font-size:1.1em;font-weight:bold;color:#0366d6'>{ticker}</span>
                    </div>
                    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### ➕ Add a Stock")
    with st.form(key="add_stock_form", clear_on_submit=True):
        new_ticker = st.text_input("Stock Ticker (e.g., RELIANCE.NS)", key="add_ticker")
        add_clicked = st.form_submit_button("Save Stock")
        if add_clicked and new_ticker:
            r = api_post("/stocks/save", token, params={"ticker": new_ticker})
            if r.ok:
                st.success(r.json().get("msg", "Saved"))
                st.rerun()  # Auto-refresh after adding
            else:
                st.error("Could not save. Please try again.")

    st.divider()
    st.markdown("### 🗑️ Remove a Stock")
    if tickers:
        with st.form(key="remove_stock_form"):
            ticker_to_remove = st.selectbox("Select stock to remove", tickers)
            remove_clicked = st.form_submit_button("Remove Stock")
            if remove_clicked and ticker_to_remove:
                r = api_delete("/stocks/remove", token, params={"ticker": ticker_to_remove})
                if r.ok:
                    st.success(r.json().get("msg", "Removed"))
                    st.rerun()  # Auto-refresh after removing
                else:
                    st.error("Could not remove. Please try again.")

