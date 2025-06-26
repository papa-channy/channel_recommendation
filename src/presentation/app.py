import yaml
import streamlit as st
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

from src.adapters import (
    FileDataLoader,
    DefaultPersonaGenerator,
    TorchRatingPredictor,
    GeminiContentLabeler,
    SeleniumScheduleCrawler,
)
from src.infrastructure.cache_manager import CacheManager
from src.domain.use_cases.recommend_channels_use_case import RecommendChannelsUseCase

@st.cache_resource
def setup_application() -> RecommendChannelsUseCase:
    load_dotenv()
    with open('config/default_config.yml') as f:
        config = yaml.safe_load(f)
    data_loader = FileDataLoader(config)
    movielens = data_loader.get_processed_movielens_data()
    persona_gen = DefaultPersonaGenerator(config, movielens)
    rating_predictor = TorchRatingPredictor(config)
    cache = CacheManager()
    labeler = GeminiContentLabeler(config, cache)
    crawler = SeleniumScheduleCrawler(config)
    embedding_model = SentenceTransformer(config['paths']['embedding_model_name'])
    return RecommendChannelsUseCase(
        persona_generator=persona_gen,
        rating_predictor=rating_predictor,
        content_labeler=labeler,
        schedule_crawler=crawler,
        embedding_model=embedding_model,
    )

try:
    use_case = setup_application()
except Exception as e:
    st.error(f'Initialization failed: {e}')
    st.stop()

st.title('TV Channel Recommendation')
persona = st.selectbox('Persona', options=['demo'])
date = st.date_input('Date')

if st.button('Recommend'):
    with st.spinner('Running recommendation...'):
        result = use_case.execute(persona, date.strftime('%Y-%m-%d'))
        st.write(result.json())
