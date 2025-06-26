import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model
from src.domain.interfaces.rating_predictor_interface import RatingPredictorInterface

class KerasRatingPredictor(RatingPredictorInterface):
    def __init__(self, model_path: str):
        self.model = load_model(model_path)
        # 사용자/영화 ID와 인덱스를 매핑하는 로직 추가 필요
        # self.user_to_index = ...
        # self.movie_to_index = ...

    def predict(self, user_id: int, movie_id: int) -> float:
        # ID를 모델이 사용하는 인덱스로 변환
        user_idx = self.user_to_index.get(user_id)
        movie_idx = self.movie_to_index.get(movie_id)

        if user_idx is None or movie_idx is None:
            return 0.0 # 기본 평점 또는 예외 처리

        # 예측 수행
        prediction = self.model.predict([np.array([user_idx]), np.array([movie_idx])])
        return prediction[0][0]