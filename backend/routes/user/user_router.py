from fastapi import APIRouter, Depends, HTTPException
from backend.db.mongo import db
from backend.routes.auth.auth_router import get_current_user
from backend.utils.hash import hash_password
from datetime import datetime
router = APIRouter()

@router.delete("/account/delete")
async def delete_account(user=Depends(get_current_user)):
    user_id = user["_id"]
    await db.users.delete_one({"_id": user_id})
    await db.watchlists.delete_many({"user_id": str(user_id)})
    return {"msg": "Account deleted"}

@router.put("/profile/email")
async def update_email(new_email: str, user=Depends(get_current_user)):
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"email": new_email}})
    return {"msg": "Email updated"}

@router.put("/profile/password")
async def update_password(new_password: str, user=Depends(get_current_user)):
    hashed = hash_password(new_password)
    await db.users.update_one({"_id": user["_id"]}, {"$set": {"password_hash": hashed}})
    return {"msg": "Password updated"}

@router.post("/save_search")
async def save_search(ticker: str, user=Depends(get_current_user)):
    user_id = str(user["_id"])
    activity = {"timestamp": datetime.utcnow().isoformat(), "action": "search", "ticker": ticker}
    alog = await db.activity_logs.find_one({"user_id": user_id})
    if alog:
        await db.activity_logs.update_one({"user_id": user_id}, {"$push": {"activities": activity}})
    else:
        await db.activity_logs.insert_one({"user_id": user_id, "activities": [activity]})
    return {"msg": f"Search for {ticker} saved"}

@router.delete("/clear")
async def clear_activity(user=Depends(get_current_user)):
    user_id = str(user["_id"])
    await db.activity_logs.delete_one({"user_id": user_id})
    return {"msg": "Activity log cleared"}

@router.get("/log")
async def get_activity(user=Depends(get_current_user)):
    user_id = str(user["_id"])
    alog = await db.activity_logs.find_one({"user_id": user_id})
    return alog["activities"] if alog else []