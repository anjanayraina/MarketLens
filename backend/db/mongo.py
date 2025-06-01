import os
from dotenv import load_dotenv

def load_env():
    app_env = os.getenv("APP_ENV", "local").lower()
    env_file = "env.prod" if app_env == "prod" else "env.local"
    env_path = os.path.join(os.path.dirname(__file__), "..", "resources", env_file)
    env_path = os.path.abspath(env_path)
    if os.path.exists(env_path):
        load_dotenv(dotenv_path=env_path)
        print(f"Loaded environment from {env_file}")
    else:
        print(f"Warning: {env_file} not found in resources/. Using defaults.")

load_env()

from motor.motor_asyncio import AsyncIOMotorClient

MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URI)
db = client["investor_insight"]
