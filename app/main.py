from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.api.chat import router as chat_router
from app.api.courses import router as courses_router
from app.api.auth import router as auth_router
from app.api.user import router as user_router
from app.seed_data import create_seed_data

@asynccontextmanager
async def lifespan(app: FastAPI):
    # await create_seed_data()
        
    yield
    print("🛑 Ứng dụng đang tắt...")

app = FastAPI(
    title="E-Learning AI Assistant",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://video-learning-assistant-fe.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn router
app.include_router(chat_router)
app.include_router(courses_router)
app.include_router(auth_router)
app.include_router(user_router)