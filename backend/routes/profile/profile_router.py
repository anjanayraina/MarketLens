from fastapi import APIRouter, Depends, HTTPException
from backend.db.mongo import db
from backend.routes.auth.auth_router import get_current_user

router = APIRouter()

@router.get("/me")
async def get_profile(user=Depends(get_current_user)):
    profile = user.get("profile", {})
    return profile

@router.put("/update")
async def update_profile(profile: dict, user=Depends(get_current_user)):
    user_id = user["_id"]
    await db.users.update_one({"_id": user_id}, {"$set": {"profile": profile}})
    return {"msg": "Profile updated", "profile": profile}
