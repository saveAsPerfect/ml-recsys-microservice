from fastapi import FastAPI
from app.api.recommendations import router as rec_router

app = FastAPI()
app.include_router(rec_router)