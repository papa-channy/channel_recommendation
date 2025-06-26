import random
from typing import Dict, List
import pandas as pd
from src.domain.interfaces import PersonaGeneratorInterface

class DefaultPersonaGenerator(PersonaGeneratorInterface):
    def __init__(self, config: dict, movielens_df: pd.DataFrame):
        self.movielens = movielens_df
        self.personas: Dict[str, Dict] = config.get('personas', {})

    def generate_dummy_watch_history(self, persona_id: str, num_records: int = 20) -> pd.DataFrame:
        persona = self.personas.get(persona_id)
        if not persona:
            raise ValueError(f'Unknown persona {persona_id}')
        favorite_genres: List[str] = persona.get('favorite_genres', [])
        sample = self.movielens.sample(num_records, replace=True).reset_index(drop=True)
        ratings = []
        for _, row in sample.iterrows():
            genres = row['genres'] if isinstance(row['genres'], list) else row['genres'].split('|')
            is_fav = any(g in genres for g in favorite_genres)
            if is_fav:
                rating = random.uniform(3.5, 5.0)
            else:
                rating = random.uniform(2.5, 4.0)
            ratings.append(round(rating * 2) / 2)
        sample['rating'] = ratings
        return sample[['movie_id', 'title', 'rating', 'genres']]
