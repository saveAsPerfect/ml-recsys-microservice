from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.schemas.schemas import PostGet,Response
from typing import List
from datetime import datetime
from app.models.models import Post, Feed
from app.core.recommender import RecommenderService
from app.core.model_loader import load_models
from app.core.features import load_features


router = APIRouter()

user_features = load_features("SELECT * FROM public.user_data") 
post_features = load_features("SELECT * FROM public.post_text_df") 

model_control, model_test = load_models()

recommender_service = RecommenderService(
    model_control=model_control,
    model_test=model_test,
    user_features=user_features,
    post_features = post_features
    )


@router.get("/post/recommendations/", response_model=Response)
def recommended_posts(user_id: int, time: datetime, limit: int = 5, db: Session = Depends(get_db)):
    # user liked posts
    liked_post_ids = [
        row[0] for row in (
            db.query(Feed.post_id)
            .filter(Feed.user_id == user_id, Feed.action == "like")
            .distinct()
            .all()
        )
    ]

    # get recs from service 
    rec_posts, exp_group = recommender_service.recommend(user_id, time, liked_post_ids, limit)

    # return posts
    recommendations = db.query(Post).filter(Post.id.in_(rec_posts)).all()

    response = Response(exp_group=exp_group, recommendations=recommendations)

    return response
