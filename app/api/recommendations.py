from fastapi import APIRouter, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.core.recommender import recommend_posts
from app.schemas.schemas import PostGet
from typing import List

router = APIRouter()


@router.get("/post/recommendations/", response_model=List[PostGet])
def recommended_posts(id: int, time: datetime, limit: int = 5, db: Session = Depends(get_db)):
    return recommend_posts(user_id=id, time=time, limit=limit, db=db)
