from typing import Dict, List
from src.domain.interfaces import RatingPredictorInterface

class TorchRatingPredictor(RatingPredictorInterface):
    def __init__(self, config: dict):
        self.default_rating = config.get('default_rating', 3.0)

    def predict_ratings(self, user_id: int, movie_ids: List[int]) -> Dict[int, float]:
        # Placeholder implementation replacing deep learning model
        return {m_id: self.default_rating for m_id in movie_ids}
