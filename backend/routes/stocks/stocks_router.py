from fastapi import APIRouter, Depends, HTTPException
from backend.db.mongo import db
from backend.routes.auth.auth_router import get_current_user
from bson import ObjectId

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
