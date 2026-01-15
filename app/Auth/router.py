from fastapi import APIRouter, HTTPException, status , Body
from .schemas import UserLogin, Token
from fastapi import Depends
from .utils import create_access_token
from .helper import authenticate_user, get_current_user
from pydantic import EmailStr
from app.database import get_db, Database
from passlib.context import CryptContext
from datetime import timedelta
import os
from dotenv import load_dotenv



router = APIRouter()

load_dotenv()
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30)) 

@router.post("/login", response_model=Token)
def login(credentials: UserLogin):
    user = authenticate_user(credentials.email, credentials.password)
    # print("User:-", user)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user's actual role from database
    actual_role = user.get("role", "employee")
    
    # If user selected a role, validate it matches their actual role
    if credentials.role:
        # Normalize role comparison (handle case differences)
        selected_role = credentials.role.lower()
        db_role = actual_role.lower()
        
        if selected_role != db_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. You selected '{credentials.role}' role but your account is registered as '{actual_role}'. Please select the correct role or contact HR."
            )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={
        "sub": credentials.email,
        "role": actual_role
        },
        expires_delta=access_token_expires)
   
    # print("Access Token:-", access_token)
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": actual_role
    }


###############################################################################
# --------create HR once route to manually add her/HR in database-----------

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

@router.post("/create_hr_once")
def create_hr_once(email: EmailStr = Body(...),password: str = Body(...),db: Database = Depends(get_db)):
    existing_hr = db["employee_db"].find_one({"role": "HR"})
    if existing_hr:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="HR already exists. This route is disabled now."
        )

    # Insert HR user
    hashed_password = pwd_context.hash(password)

    db["employee_db"].insert_one({
        "email": email,
        "password": hashed_password, 
        "role": "HR"
    })

    return {"msg": "HR account created successfully"}




@router.get("/me")
def read_me(current_user: dict = Depends(get_current_user)):              #depend = its works as a middleware between the request from the client and the actual endpoint matlab the current_user variable will contain the user information if the token is valid
    return current_user

