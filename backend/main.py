from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.auth_router import router as auth_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])

@app.get("/")
def root():
    return {"msg": "Investor Insight backend running!"}
