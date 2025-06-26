from datetime import datetime, timedelta
from typing import Any, Dict, List
from src.domain.interfaces import ScheduleCrawlerInterface

class SeleniumScheduleCrawler(ScheduleCrawlerInterface):
    def __init__(self, config: dict):
        self.config = config

    def fetch_schedule(self, target_date: str) -> List[Dict[str, Any]]:
        # Placeholder implementation
        start = datetime.strptime(target_date, '%Y-%m-%d')
        return [
            {
                'channel_name': 'DemoChannel',
                'title': 'Demo Program',
                'start_time': start,
                'end_time': start + timedelta(hours=1),
                'synopsis': 'demo',
            }
        ]
