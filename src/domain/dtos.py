from datetime import datetime
from typing import List, Dict, Optional
from pydantic import BaseModel, Field

class WatchedMovieDTO(BaseModel):
    movie_id: int
    title: str
    rating: float

class LabelledContentDTO(BaseModel):
    title: str
    labels: List[str]
    predicted_rating: Optional[float] = None

class RecommendedProgramDTO(BaseModel):
    channel: str
    title: str
    start_time: datetime
    end_time: datetime
    similarity_score: float = Field(..., ge=0, le=1)
    reason: str

class RecommendationResultDTO(BaseModel):
    persona_name: str
    persona_description: str
    watch_history: List[WatchedMovieDTO]
    preference_cluster: List[LabelledContentDTO]
    recommended_programs: List[RecommendedProgramDTO]
