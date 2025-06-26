import os
from typing import List
from dotenv import load_dotenv
from src.domain.interfaces import ContentLabelerInterface
from src.infrastructure.cache_manager import CacheManager

class GeminiContentLabeler(ContentLabelerInterface):
    def __init__(self, config: dict, cache: CacheManager | None = None) -> None:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not set in environment")
        self.api_key = api_key
        self.cache = cache
        self.default_labels = config.get("default_labels", [])

    def generate_labels(self, title: str, overview: str) -> List[str]:
        cache_key = f'{title}:{overview}'
        if self.cache:
            cached = self.cache.get_labels(cache_key)
            if cached:
                return cached
        # Placeholder for API call
        labels = self.default_labels
        if self.cache:
            self.cache.save_labels(cache_key, labels)
        return labels
