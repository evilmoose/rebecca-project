from fastapi import FastAPI
from routes.auth_route import auth_router
from routes.chat_route import chat_router
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

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
