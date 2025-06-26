import os
from typing import List
from dotenv import load_dotenv
from src.domain.interfaces import ContentLabelerInterface
from src.infrastructure.redis_cache_manager import CacheManager

class GeminiContentLabeler(ContentLabelerInterface):
    def __init__(self, config: dict, cache: CacheManager | None = None):
        load_dotenv()
        self.cache = cache
        self.default_labels = config.get('default_labels', [])

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
