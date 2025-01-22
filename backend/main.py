from fastapi import FastAPI, Depends
from routes.auth_route import auth_router
from routes.chat_route import chat_router
from fastapi.middleware.cors import CORSMiddleware
import redis
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Initialize Redis client
redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router, prefix="/auth")
app.include_router(chat_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "FastAPI application is running"}

#  uvicorn main:app --host 127.0.0.1 --port 5000    
