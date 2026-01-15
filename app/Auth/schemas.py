from pydantic import BaseModel, EmailStr,field_validator
from typing import Optional, Dict, Any
import re



class UserLogin(BaseModel):
    email: EmailStr
    password: str
    role: Optional[str] = None  


class Token(BaseModel):
    access_token: str
    token_type: str
    role : str | None = None
