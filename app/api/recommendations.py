from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.database import get_db
from app.schemas.schemas import Response
from app.models.models import Post, Feed
from app.core.recommender import RecommenderService
from app.core.model_loader import load_models
from app.core.features import load_features
from app.core.logging_config import get_logger
from app.config import USER_FEATURES_QUERY, POST_FEATURES_QUERY

logger = get_logger(__name__)

router = APIRouter()

# Global variables (will be initialized in startup event)
user_features = None
post_features = None
model_control = None
model_test = None
recommender_service = None


def initialize_services():
    """Initialize models and features - called during startup"""
    global user_features, post_features, model_control, model_test, recommender_service

    logger.info("Initializing recommendation services")

    try:
        # Load features using configurable SQL queries
        logger.info("Loading user features")
        user_features = load_features(USER_FEATURES_QUERY)

        logger.info("Loading post features")
        post_features = load_features(POST_FEATURES_QUERY)

        # Load models
        logger.info("Loading ML models")
        model_control, model_test = load_models()

        # Initialize recommender service
        logger.info("Initializing recommender service")
        recommender_service = RecommenderService(
            model_control=model_control,
            model_test=model_test,
            user_features=user_features,
            post_features=post_features
        )

        logger.info("All services initialized successfully")

    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise


@router.get("/post/recommendations/", response_model=Response)
def recommended_posts(user_id: int, time: datetime, limit: int = 5, db: Session = Depends(get_db)):
    """Get post recommendations for a user"""
    logger.info(f"Received recommendation request for user {user_id}")

    # Validate input parameters
    if limit <= 0 or limit > 100:
        raise HTTPException(
            status_code=400, detail="Limit must be between 1 and 100")

    try:
        # Get user liked posts
        logger.debug(f"Fetching liked posts for user {user_id}")
        liked_post_ids = [
            row[0] for row in (
                db.query(Feed.post_id)
                .filter(Feed.user_id == user_id, Feed.action == "like")
                .distinct()
                .all()
            )
        ]
        logger.debug(
            f"Found {len(liked_post_ids)} liked posts for user {user_id}")

        # Get recommendations from service
        try:
            rec_posts, exp_group = recommender_service.recommend(
                user_id, time, liked_post_ids, limit)
        except KeyError:
            logger.warning(f"User {user_id} not found in features")
            raise HTTPException(
                status_code=404, detail=f"User {user_id} not found")
        except Exception as e:
            logger.error(
                f"Recommendation generation failed for user {user_id}: {e}")
            raise HTTPException(
                status_code=500, detail="Failed to generate recommendations")

        # Get post details from database
        logger.debug(
            f"Fetching {len(rec_posts)} recommended posts from database")
        recommendations = db.query(Post).filter(Post.id.in_(rec_posts)).all()

        response = Response(exp_group=exp_group,
                            recommendations=recommendations)
        logger.info(
            f"Successfully generated {len(recommendations)} recommendations for user {user_id}")

        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in recommendation endpoint: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
