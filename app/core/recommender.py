# from app.core.ab_testing import get_exp_group
from fastapi import Depends
from app.db.database import get_db
from datetime import datetime
from app.models.models import Post, Feed
from app.schemas.schemas import PostGet
from sqlalchemy.orm import Session


def recommend_posts(user_id: int, time: datetime, limit: int = 5, db: Session = Depends(get_db)):

    post_ids = [1141, 1634, 1707, 1883, 1685]
    recs = db.query(Post).filter(Post.id.in_(post_ids)).all()
    return recs
