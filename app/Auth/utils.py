import bcrypt
from passlib.context import CryptContext
from datetime import datetime, timedelta , timezone
from jose import jwt, JWTError
import os
from dotenv import load_dotenv
from app.database import get_db

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")

def hash_password(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str):
    try:
        result = bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        print(f" Verification result: {result}")
        return result
    except Exception as e:
        print(f" Bcrypt error: {e}")
        return False


def create_access_token(data: dict, expires_delta: timedelta | None = None ):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes = 30)                         
    to_encode.update({
                      "exp": expire,
                      "sub": data.get("sub"),                              
                      "role": data.get("role")
                      })                                                   # sub is subject, inside it we store user identification like email or id so that we can identify user from token if the person trying to access anyy route is authenticated or not 
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
  


def get_user_by_email(email: str):
    db = get_db()
    user_collection = db["employee_db"]
    return user_collection.find_one({"email": email})




