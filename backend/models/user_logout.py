from pydantic import BaseModel, EmailStr

class UserOut(BaseModel):
    username: str
    email: EmailStr