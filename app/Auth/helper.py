from typing import Optional, Dict, Any
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, field_validator
import os
import re
from dotenv import load_dotenv
from .utils import get_user_by_email, verify_password, hash_password

load_dotenv()

ALLOWED_DOMAINS = ["sunfocus.com", "erp.com", "gmail.com", "outlook.com", "yahoo.com", "hotmail.com", "test.com"]

class EmailPasswordValidator(BaseModel):
    email: EmailStr
    password: str  

    @field_validator('password')
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r'[^A-Za-z0-9]', v):
            raise ValueError('Password must contain at least one special character')
        return v

    @field_validator('email')
    def validate_email_domain(cls, v):
        """Validate that the email domain is in the allowed list"""
        domain = v.split('@')[-1]
        if domain not in ALLOWED_DOMAINS:
            raise ValueError(f"Email domain '{domain}' is not allowed.")
        return v
    
    model_config = {"extra": "forbid"}
    
# Security configuration
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#=========================== Authentication functions=========================================================
def authenticate_user(email: str, password: str) -> Optional[Dict[str, Any]]:
    try:
        print(f"[AUTH] Attempting to authenticate user: {email}")
        
        # Get user from database
        user = get_user_by_email(email)
        if not user:
            print(f"[AUTH] User not found: {email}")
            return None
            
        print(f"[AUTH] User found, verifying password...")
        if not verify_password(password, user["password"]):
            print(f"[AUTH] Invalid password for user: {email}")
            return None
            
        print(f"[AUTH] Successfully authenticated user: {email}")
        return user
        
    except Exception as e:
        print(f"[AUTH] Error during authentication: {str(e)}")
        return None

#==============================GET CURRENT USER ================================================================================
async def get_current_user(authorization: str = Header(...)) -> Dict[str, Any]:
    """
    Dependency to get the current user from the JWT token.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required or invalid",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    email: str = payload.get("sub")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject (sub)",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = get_user_by_email(email)     # Get user from database
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if user.get('disabled', False):    # Check if user is active
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is disabled"
        )
    
    return user

#==============================================================================================================
