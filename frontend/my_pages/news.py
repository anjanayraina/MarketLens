import streamlit as st
from frontend.utils.news import fetch_google_news

def news_page():
    st.title("📰 Stock News Search")
    stock = st.text_input("Enter Stock Name or Symbol (e.g., RELIANCE)", "")
    if stock:
        news = fetch_google_news(stock)
        if news:
            for n in news:
                st.markdown(f"**[{n['title']}]({n['link']})**  \n<sub>{n['published']}</sub>", unsafe_allow_html=True)
                st.write(n['summary'])
                st.divider()
        else:
            st.info("No news found for this stock.")
