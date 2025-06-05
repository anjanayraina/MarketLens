import streamlit as st
from frontend.utils.news import fetch_google_news

def news_page():
    st.title("📰 Stock News Search")
    stock = st.text_input("Enter Stock Name or Symbol (e.g., RELIANCE)", "")
    if stock:
        sort_order = st.selectbox(
            "Sort By",
            ["Newest", "Positive First", "Negative First"],
            index=0,
        )
        news = fetch_google_news(stock)
        if news:
            if sort_order == "Positive First":
                news.sort(key=lambda x: x["sentiment"], reverse=True)
            elif sort_order == "Negative First":
                news.sort(key=lambda x: x["sentiment"])
            for n in news:
                st.markdown(
                    f"**[{n['title']}]({n['link']})**  \n<sub>{n['published']}</sub>",
                    unsafe_allow_html=True,
                )
                st.write(n["summary"])
                sentiment_text = (
                    "⬆️" if n["sentiment"] > 0 else "⬇️" if n["sentiment"] < 0 else "➖"
                )
                st.write(f"Sentiment Score: {n['sentiment']:.2f} {sentiment_text}")
                st.divider()
        else:
            st.info("No news found for this stock.")

