from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import connect_to_mongo, close_mongo_connection
from app.routes.auth import router as auth_router # <-- IMPORT NEW AUTH ROUTER
from app.routes.plan import router as plan_router
from app.routes.chat import router as chat_router
from app.routes.tasks import router as tasks_router
from app.routes.progress import router as progress_router
from app.routes.profile import router as profile_router
from app.routes.food import router as food_router
from app.routes.document import router as document_router
from app.routes.voice import router as voice_router
from app.routes.notifications import router as notifications_router
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Handles application startup and shutdown events.
    """
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title="FitnessAI",
    description="A smart assistant for personalized fitness and nutrition plans.",
    version="1.0.0",
    lifespan=lifespan
)
# origins = ["http://localhost:5173"]  # <-- Add your frontend URL here
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router) # <-- INCLUDE NEW AUTH ROUTER
app.include_router(profile_router)
app.include_router(plan_router)
app.include_router(chat_router)
app.include_router(tasks_router)
app.include_router(progress_router)
app.include_router(food_router)
app.include_router(document_router)
app.include_router(voice_router)
app.include_router(notifications_router)

@app.get("/", tags=["Root"])
def read_root():
    """A simple endpoint to check if the backend is running."""
    return {"message": "Welcome to the Fitness AI backend. We are up and running!"}