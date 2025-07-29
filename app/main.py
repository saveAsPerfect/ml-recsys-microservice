from fastapi import FastAPI
from app.api.recommendations import router as rec_router

app = FastAPI(
    title="ML Post Recommender",
    description="Microservice for recommending posts",
)

app.include_router(rec_router)
