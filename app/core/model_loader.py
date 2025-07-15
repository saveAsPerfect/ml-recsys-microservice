from catboost import CatBoostClassifier


def load_model(name: str) -> CatBoostClassifier:
    model = CatBoostClassifier()
    model.load_model(name)
    return model


# model_control = load_model("draft_model_ver_1")
# model_test = load_model("draft_model")
