from abc import ABC, abstractmethod
from typing import Any, Dict, List

class ScheduleCrawlerInterface(ABC):
    @abstractmethod
    def fetch_schedule(self, target_date: str) -> List[Dict[str, Any]]:
        """Fetch IPTV schedule for a given date."""
        raise NotImplementedError
