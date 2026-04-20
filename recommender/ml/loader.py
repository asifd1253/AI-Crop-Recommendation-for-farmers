import os
import pickle
from functools import lru_cache

from django.conf import settings

@lru_cache(maxsize=1)
def load_bundle():
    pkl_path = os.path.join(settings.BASE_DIR, 'recommender', 'ml', 'Crop_recommendation_RF.pkl')

    with open(pkl_path, "rb") as f:
        bundle = pickle.load(f)

    assert "model" in bundle and "features_cols" in bundle, "Invalid bundle format."
    return bundle

def predict_crop(features_dict):
    bundle = load_bundle()
    model = bundle["model"]
    order = bundle["features_cols"]

    X = [[float(features_dict[c]) for c in order]]
    pred = model.predict(X)
    return pred[0]