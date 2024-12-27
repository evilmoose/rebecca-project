from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from utils.db_utils import connect_db
import jwt
import bcrypt
import os

auth_router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str

@auth_router.post("/login")
async def login(request: LoginRequest):
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE username = %s", (request.username,))
    user = cursor.fetchone()
    cursor.close()

    if not user or not bcrypt.checkpw(request.password.encode("utf-8"), user["password_hash"].encode("utf-8")):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = jwt.encode({"username": request.username}, os.getenv("SECRET_KEY"), algorithm="HS256")
    return {"token": token, "username": request.username}

@auth_router.post("/register")
async def register(request: RegisterRequest):
    db = connect_db()
    cursor = db.cursor()
    hashed_password = bcrypt.hashpw(request.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    cursor.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (request.username, hashed_password))
    db.commit()
    cursor.close()

    return {"message": "User registered successfully"}
