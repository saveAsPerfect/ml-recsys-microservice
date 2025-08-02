from app.core.ab_testing import get_exp_group
from app.core.features import build_features
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class RecommenderService:
    def __init__(self, model_control, model_test, user_features, post_features):
        self.model_control = model_control
        self.model_test = model_test
        self.user_features = user_features
        self.post_features = post_features
        logger.info("RecommenderService initialized successfully")

    def recommend(self, user_id, time, liked_posts, limit=5):
        """Generate recommendations for a user"""
        logger.info(f"Generating recommendations for user {user_id}")

        # Validate input parameters
        if limit <= 0:
            raise ValueError("Limit must be positive")
        if not isinstance(liked_posts, list):
            liked_posts = list(liked_posts)

        # Get experiment group
        exp_group = get_exp_group(user_id)
        logger.debug(
            f"User {user_id} assigned to experiment group: {exp_group}")

        model = self.model_control if exp_group == "control" else self.model_test

        # Build features
        logger.debug(f"Building features for user {user_id}")
        df = build_features(user_id, self.post_features,
                            self.user_features, time)

        # Remove liked posts
        df = df[~df["post_id"].isin(liked_posts)]
        if df.empty:
            logger.warning(
                f"No recommendations available for user {user_id} - empty dataframe after filtering")
            return [], exp_group  # fallback

        # Predict from model
        try:
            cols = list(model.feature_names_)
            df["score"] = model.predict(df[cols])
            logger.debug(f"Generated predictions for {len(df)} posts")
        except Exception as e:
            logger.error(f"Prediction failed for user {user_id}: {e}")
            return [], exp_group

        # Sort predictions and get top posts
        top_posts = (
            df.sort_values("score", ascending=False)["post_id"]
            .head(limit)
            .tolist()
        )

        logger.info(
            f"Generated {len(top_posts)} recommendations for user {user_id} in group {exp_group}")
        return top_posts, exp_group
