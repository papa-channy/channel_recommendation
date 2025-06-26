from __future__ import annotations

from typing import List

from ..dtos import RecommendationResultDTO, WatchedMovieDTO, LabelledContentDTO, RecommendedProgramDTO
from ..interfaces import (
    PersonaGeneratorInterface,
    RatingPredictorInterface,
    ContentLabelerInterface,
    ScheduleCrawlerInterface,
)

class RecommendChannelsUseCase:
    """Orchestrates recommendation flow."""

    def __init__(
        self,
        persona_generator: PersonaGeneratorInterface,
        rating_predictor: RatingPredictorInterface,
        content_labeler: ContentLabelerInterface,
        schedule_crawler: ScheduleCrawlerInterface,
        embedding_model,
    ) -> None:
        self.persona_gen = persona_generator
        self.rating_predictor = rating_predictor
        self.labeler = content_labeler
        self.crawler = schedule_crawler
        self.embedding_model = embedding_model

    def execute(self, persona_id: str, target_date: str) -> RecommendationResultDTO:
        history_df = self.persona_gen.generate_dummy_watch_history(persona_id)
        movie_ids = history_df['movie_id'].tolist()
        predicted = self.rating_predictor.predict_ratings(0, movie_ids)

        labelled_movies: List[LabelledContentDTO] = []
        for _, row in history_df.iterrows():
            labels = self.labeler.generate_labels(row['title'], row.get('overview', ''))
            labelled_movies.append(LabelledContentDTO(title=row['title'], labels=labels, predicted_rating=predicted.get(row['movie_id'])))

        schedule = self.crawler.fetch_schedule(target_date)
        recommended_programs: List[RecommendedProgramDTO] = []
        for item in schedule:
            labels = self.labeler.generate_labels(item['title'], item.get('synopsis', ''))
            # dummy similarity score
            similarity = 0.5
            recommended_programs.append(
                RecommendedProgramDTO(
                    channel=item['channel_name'],
                    title=item['title'],
                    start_time=item['start_time'],
                    end_time=item['end_time'],
                    similarity_score=similarity,
                    reason='demo',
                )
            )

        watch_history = [WatchedMovieDTO(movie_id=row['movie_id'], title=row['title'], rating=row['rating']) for _, row in history_df.iterrows()]

        return RecommendationResultDTO(
            persona_name=persona_id,
            persona_description='demo persona',
            watch_history=watch_history,
            preference_cluster=labelled_movies,
            recommended_programs=recommended_programs,
        )
