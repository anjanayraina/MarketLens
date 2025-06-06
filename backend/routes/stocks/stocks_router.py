from fastapi import APIRouter, Depends, HTTPException
from backend.db.mongo import db
from backend.routes.auth.auth_router import get_current_user
from fastapi import APIRouter, Depends, Query
from bson import ObjectId
import requests
from backend.utils.data_processing import make_serializable , parse_peers_html, make_json_serializable, clean_json
import httpx
import numpy as np
import yfinance as yf
import pandas as pd
router = APIRouter()

@router.post("/save")
async def save_stock(ticker: str, user=Depends(get_current_user)):
    user_id = str(user["_id"])
    wl = await db.watchlists.find_one({"user_id": user_id})
    if wl:
        if ticker in wl["tickers"]:
            return {"msg": "Already saved"}
        await db.watchlists.update_one({"user_id": user_id}, {"$push": {"tickers": ticker}})
    else:
        await db.watchlists.insert_one({"user_id": user_id, "tickers": [ticker]})
    return {"msg": f"{ticker} saved"}

@router.get("/list")
async def list_stocks(user=Depends(get_current_user)):
    user_id = str(user["_id"])
    wl = await db.watchlists.find_one({"user_id": user_id})
    return wl["tickers"] if wl else []

@router.delete("/remove")
async def remove_stock(ticker: str, user=Depends(get_current_user)):
    user_id = str(user["_id"])
    wl = await db.watchlists.find_one({"user_id": user_id})
    if not wl or ticker not in wl["tickers"]:
        raise HTTPException(status_code=404, detail="Ticker not found in watchlist")
    await db.watchlists.update_one({"user_id": user_id}, {"$pull": {"tickers": ticker}})
    return {"msg": f"{ticker} removed"}

@router.get("/peers/{company_id}")
async def get_peers(company_id: str):
    # Step 1: Fetch HTML from Screener
    company_id = "6598250"  # Example: Map ticker to company_id

    url = f"https://www.screener.in/api/company/{company_id}/peers/"
    response = requests.get(url)
    if response.status_code != 200:
        return {"error": "Failed to fetch data from Screener"}

    # Step 2: Parse the HTML and return JSON
    html = response.content.decode()
    peers = parse_peers_html(html)
    return peers

@router.get("/ohlc")
async def get_ohlc(
    ticker: str,
    period: str = Query("6mo", enum=["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"]),
    interval: str = Query("1d", enum=["1m", "5m", "15m", "1h", "1d", "1wk"])
):
    if not ticker:
        return {"error": "Ticker is required"}
    df = yf.download(ticker, period=period, interval=interval)
    if df.empty:
        return []

    df = df.reset_index()

    # --- FLATTEN MULTIINDEX COLUMNS ---
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [
            '_'.join([str(l) for l in tup if l and l != '']) for tup in df.columns.values
        ]
    else:
        df.columns = [str(col) for col in df.columns]

    # MAP BACK TO SIMPLE COLUMN NAMES
    simple_map = {
        k: k for k in ["Date", "Open", "High", "Low", "Close", "Volume", "MA20", "MA50"]
    }
    # Try to detect common yfinance patterns and simplify:
    for col in df.columns:
        for field in ["Open", "High", "Low", "Close", "Volume"]:
            if field in col:
                simple_map[col] = field
        if "Date" in col or "index" in col:
            simple_map[col] = "Date"

    df = df.rename(columns=simple_map)

    # Clean: Only keep rows where 'Date' is present and valid
    if "Date" in df.columns:
        df = df[pd.to_datetime(df["Date"], errors="coerce").notnull()]
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%Y-%m-%d")
    else:
        # fallback: first column as date
        date_col = df.columns[0]
        df = df[pd.to_datetime(df[date_col], errors="coerce").notnull()]
        df["Date"] = pd.to_datetime(df[date_col]).dt.strftime("%Y-%m-%d")

    # Calculate moving averages
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()

    output_cols = ["Date", "Open", "High", "Low", "Close", "Volume", "MA20", "MA50"]
    for col in output_cols:
        if col not in df.columns:
            df[col] = [None] * len(df)

    df = df[output_cols]
    df = df.replace([np.inf, -np.inf], np.nan)

    # --- SERIALIZE FOR JSON ---
    records = []
    for _, row in df.iterrows():
        record = {col: make_serializable(row[col]) for col in output_cols}
        records.append(record)
    return records
@router.post("/advice")
async def get_advice(tickers: list, risk: str, horizon: str):
    prompt = f"User wants advice for {tickers}, risk: {risk}, horizon: {horizon}"
    # Call OpenAI API here and return response
    return {"advice": "Buy RELIANCE.NS, Hold INFY.NS"}


@router.get("/indicators")
async def get_indicators(ticker: str, period: str = "1mo"):
    df = yf.download(ticker, period=period)
    if df.empty:
        return []
    # ----------- FIX: Flatten MultiIndex columns -----------
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]
    # -------------------------------------------------------
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df = df.reset_index()

    cols = ["Close", "MA20", "MA50"]
    for candidate in ["Date", "Datetime", "index"]:
        if candidate in df.columns:
            cols.append(candidate)
            break

    records = []
    for _, row in df[cols].iterrows():
        record = {str(col): row[col] for col in cols}
        records.append(clean_json(record))
    return records