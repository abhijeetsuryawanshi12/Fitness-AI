from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db import connect_to_mongo, close_mongo_connection
from app.routes.onboarding import router as onboarding_router
from app.routes.plan import router as plan_router
from app.routes.chat import router as chat_router
from app.routes.tasks import router as tasks_router
from app.routes.progress import router as progress_router
from app.routes.profile import router as profile_router
from app.routes.food import router as food_router # <-- IMPORT NEW ROUTER
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(onboarding_router)
app.include_router(profile_router)
app.include_router(plan_router)
app.include_router(chat_router)
app.include_router(tasks_router)
app.include_router(progress_router)
app.include_router(food_router) # <-- INCLUDE NEW ROUTER

@app.get("/", tags=["Root"])
def read_root():
    """A simple endpoint to check if the backend is running."""
    return {"message": "Welcome to the Fitness AI backend. We are up and running!"}