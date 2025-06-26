from abc import ABC, abstractmethod
from typing import Dict, List

class RatingPredictorInterface(ABC):
    @abstractmethod
    def predict_ratings(self, user_id: int, movie_ids: List[int]) -> Dict[int, float]:
        """Predict ratings for the given user and movie ids."""
        raise NotImplementedError
