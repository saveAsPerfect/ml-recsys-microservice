from catboost import CatBoostRanker
from catboost import CatBoostClassifier 
from app.config import MODEL_CONTROL_PATH
from app.config import MODEL_TEST_PATH


def load_models():
    model_control = CatBoostRanker()
    model_control.load_model(MODEL_CONTROL_PATH)
    model_test = CatBoostClassifier()
    model_test.load_model(MODEL_TEST_PATH)
    return model_control, model_test

model_control, model_test = load_models()

