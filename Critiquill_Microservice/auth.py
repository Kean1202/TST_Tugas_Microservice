from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import json

SECRET_KEY = ""
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15

with open("users.json", "r") as json_file:
    users_data = json.load(json_file)

# Temporary testing dict
# users_data = {
#     "kean1202": {
#         "user_id": 1,
#         "username": "kean1202",
#         "name": "Kean",
#         "password_hash": "$2b$12$mtJa18Rz1Sa9eeFYqJjbteG/18PkofTTvIE9HXyKAtmTwWUw1TeKm",
#         "disabled": 0
#     }
# }

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: str or None = None


class User(BaseModel):
    user_id: int 
    username: str
    password_preprocessed: str
    name: str or None = None
    disabled: bool or None = None

class UserCreate():
    user_id: int 
    username: str
    password_preprocessed: str
    name: str or None = None
    isTutor: bool
    isAdmin: bool
    disabled: bool or None = None


class UserInDB(User):
    user_id: int 
    username: str
    name: str or None = None
    password_preprocessed: str
    password_hash: str
    isTutor: bool
    isAdmin: bool
    disabled: bool or None = None


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth_2_scheme = OAuth2PasswordBearer(tokenUrl= 'token')

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_all_username(userlist: dict):
    user_arr = []
    for user in userlist:
        user_arr.append(user.lower())
    return user_arr


def get_user(userlist: dict, username: str):
    arr_username = get_all_username(users_data)
    if username.lower() in arr_username:
        user_data = userlist[username]
        return UserInDB(**user_data)
        
        
def authenticate_user(userlist: dict, username: str, password: str):
    user = get_user(userlist, username)
    if not user:
        return False
    if not verify_password(password, user.password_hash):
        return False
    
    return user

def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = 10)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt # the access token
