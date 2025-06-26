from abc import ABC, abstractmethod
from typing import List

class ContentLabelerInterface(ABC):
    @abstractmethod
    def generate_labels(self, title: str, overview: str) -> List[str]:
        """Generate semantic labels for given content."""
        raise NotImplementedError
