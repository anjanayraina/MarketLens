import streamlit as st
from frontend.utils.api import api_get
from frontend.utils.state import get_token
import plotly.graph_objects as go

def chart_page():
    st.title("📊 Stock Candlestick Chart")
    token = get_token()
    # Choose ticker
    ticker = st.text_input("Stock Ticker", "RELIANCE.NS")
    period = st.selectbox("Time Period", ["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"], index=4)
    interval = st.selectbox("Interval", ["1m", "5m", "15m", "1h", "1d", "1wk"], index=4)
    if st.button("Show Chart"):
        res = api_get("/stocks/ohlc", token, params={"ticker": ticker, "period": period, "interval": interval})
        data = res.json() if res.ok else []
        if not data:
            st.warning("No data found for this ticker/period.")
            return
        import pandas as pd
        df = pd.DataFrame(data)
        # Plot candlestick
        fig = go.Figure(data=[go.Candlestick(
            x=df["Date"],
            open=df["Open"],
            high=df["High"],
            low=df["Low"],
            close=df["Close"],
            name="Candlestick"
        )])
        # Add moving averages
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["MA20"], line=dict(width=1), name="MA20"
        ))
        fig.add_trace(go.Scatter(
            x=df["Date"], y=df["MA50"], line=dict(width=1), name="MA50"
        ))
        # Add volume as bar chart
        fig.add_trace(go.Bar(
            x=df["Date"], y=df["Volume"], name="Volume", marker_opacity=0.2, yaxis="y2"
        ))
        # Layout tweaks
        fig.update_layout(
            xaxis_rangeslider_visible=False,
            yaxis_title="Price",
            yaxis2=dict(
                title="Volume", overlaying="y", side="right", showgrid=False
            ),
            legend=dict(orientation="h"),
            margin=dict(l=10, r=10, t=30, b=10)
        )
        st.plotly_chart(fig, use_container_width=True)
