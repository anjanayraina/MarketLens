from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.routes.auth.auth_router import router as auth_router
from backend.routes.stocks.stocks_router import router as stocks_router
from backend.routes.profile.profile_router import router as profiles_router
from backend.routes.user.user_router import router as user_router
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(stocks_router, prefix="/stocks", tags=["stocks"])
app.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
app.include_router(user_router, prefix="/user", tags=["user"])

@app.get("/")
def root():
    return {"msg": "Investor Insight backend running!"}
