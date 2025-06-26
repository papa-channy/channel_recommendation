import pandas as pd
from src.adapters.default_persona_generator import DefaultPersonaGenerator

def test_dummy_history_gives_higher_ratings_to_favorite_genres():
    movies = pd.DataFrame({
        'movie_id': [1,2,3,4],
        'title': ['A','B','C','D'],
        'genres': ['Action|Adventure','Romance','Comedy','Drama']
    })
    config = {
        'personas': {
            'demo': {
                'favorite_genres': ['Action']
            }
        }
    }
    gen = DefaultPersonaGenerator(config, movies)
    df = gen.generate_dummy_watch_history('demo', num_records=50)
    fav = df[df['genres'].str.contains('Action')]['rating'].mean()
    others = df[~df['genres'].str.contains('Action')]['rating'].mean()
    assert fav > others
