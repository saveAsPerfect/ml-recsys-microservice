from app.core.ab_testing import get_exp_group
from app.core.features import build_features

class RecommenderService:
    def __init__(self, model_control, model_test, user_features, post_features):
        
        self.model_control = model_control
        self.model_test = model_test

        self.user_features = user_features
        self.post_features = post_features

    def recommend(self, user_id, time, liked_posts, limit=5):
        
        exp_group = get_exp_group(user_id)
        model = self.model_control if exp_group == "control" else self.model_test

        # build features
        df = build_features(user_id, self.post_features, self.user_features, time)

        # remove liked post
        df = df[~df["post_id"].isin(liked_posts)]
        if df.empty:
            return [], exp_group  # fallback 
        
        # predict from model

        cols = list(model.feature_names_)
        if exp_group == 'control':
            df["score"] = model.predict(df[cols])
        elif exp_group == 'test':
            df['score'] = model.predict_proba(df[cols])[:,1]

        # sorting predictions 
        top_posts = (
            df.sort_values("score", ascending=False)["post_id"]
            .head(limit)
            .tolist()
        )
        return top_posts, exp_group