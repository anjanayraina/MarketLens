from fastapi import APIRouter, Depends, HTTPException
from backend.db.mongo import db
from backend.routes.auth.auth_router import get_current_user
from fastapi import APIRouter, Depends, Query
from bson import ObjectId
import httpx
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


@router.get("/peers")
async def get_peers(ticker: str):
    company_id = "6598250"  # Example: Map ticker to company_id
    url = f"https://www.screener.in/api/company/{company_id}/peers/"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        r.raise_for_status()
        return r.json()


@router.get("/ohlc")
async def get_ohlc(
    ticker: str,
    period: str = Query("6mo", enum=["1d", "5d", "1mo", "3mo", "6mo", "1y", "5y", "max"]),
    interval: str = Query("1d", enum=["1m", "5m", "15m", "1h", "1d", "1wk"])
):
    # Validate ticker
    if not ticker:
        return {"error": "Ticker is required"}
    df = yf.download(ticker, period=period, interval=interval)
    if df.empty:
        return []
    df.reset_index(inplace=True)
    # Calculate moving averages
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    df = df[["Date", "Open", "High", "Low", "Close", "Volume", "MA20", "MA50"]]
    # Convert datetime to string for JSON
    df["Date"] = df["Date"].astype(str)
    return df.to_dict(orient="records")

@router.post("/advice")
async def get_advice(tickers: list, risk: str, horizon: str):
    prompt = f"User wants advice for {tickers}, risk: {risk}, horizon: {horizon}"
    # Call OpenAI API here and return response
    return {"advice": "Buy RELIANCE.NS, Hold INFY.NS"}

@router.get("/indicators")
async def get_indicators(ticker: str, period: str = "1mo"):
    df = yf.download(ticker, period=period)
    df["MA20"] = df["Close"].rolling(window=20).mean()
    df["MA50"] = df["Close"].rolling(window=50).mean()
    return df[["Close", "MA20", "MA50"]].reset_index().to_dict(orient="records")
