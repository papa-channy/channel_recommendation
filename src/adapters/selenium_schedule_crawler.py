from datetime import datetime, timedelta
import json
from pathlib import Path
from typing import Any, Dict, List

from src.domain.interfaces import ScheduleCrawlerInterface

class SeleniumScheduleCrawler(ScheduleCrawlerInterface):
    def __init__(self, config: dict) -> None:
        self.config = config
        cache_dir = config.get("paths", {}).get("schedule_cache_dir", "data/schedule_cache")
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def fetch_schedule(self, target_date: str) -> List[Dict[str, Any]]:
        file_path = self.cache_dir / f"{target_date}.json"
        if file_path.exists():
            with file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            # parse datetime strings back to datetime objects
            for item in data:
                item["start_time"] = datetime.fromisoformat(item["start_time"])
                item["end_time"] = datetime.fromisoformat(item["end_time"])
            return data

        start = datetime.strptime(target_date, "%Y-%m-%d")
        data = [
            {
                "channel_name": "DemoChannel",
                "title": "Demo Program",
                "start_time": start,
                "end_time": start + timedelta(hours=1),
                "synopsis": "demo",
            }
        ]
        with file_path.open("w", encoding="utf-8") as f:
            serializable = [
                {**item, "start_time": item["start_time"].isoformat(), "end_time": item["end_time"].isoformat()} for item in data
            ]
            json.dump(serializable, f)
        return data
