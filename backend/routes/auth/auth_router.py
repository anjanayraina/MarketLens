from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from backend.db.mongo import db
from backend.models.user_create import UserCreate
from backend.models.user_login import UserLogin
from backend.models.user_logout import UserOut
from backend.utils.hash import hash_password, verify_password
from backend.utils.jwt_handler import create_access_token, decode_access_token
from bson import ObjectId

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

@router.post("/register")
async def register(user: UserCreate):
    if await db.users.find_one({"username": user.username}):
        raise HTTPException(status_code=400, detail="Username already exists")
    if await db.users.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(user.password)
    user_dict = user.dict()
    user_dict["password_hash"] = hashed
    del user_dict["password"]
    await db.users.insert_one(user_dict)
    return {"msg": "User registered!"}

@router.post("/login")
async def login(form: UserLogin):
    user = await db.users.find_one({"username": form.username})
    if not user or not verify_password(form.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token({"user_id": str(user["_id"]), "username": user["username"]})
    return {"access_token": token}

async def get_current_user(token: str = Depends(oauth2_scheme)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await db.users.find_one({"_id": ObjectId(payload["user_id"])})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/me", response_model=UserOut)
async def get_me(user=Depends(get_current_user)):
    return {"username": user["username"], "email": user["email"]}
