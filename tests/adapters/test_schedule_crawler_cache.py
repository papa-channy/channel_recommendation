import os
from src.adapters.selenium_schedule_crawler import SeleniumScheduleCrawler


def test_schedule_file_cache(tmp_path):
    cache_dir = tmp_path / "cache"
    config = {"paths": {"schedule_cache_dir": str(cache_dir)}}
    crawler = SeleniumScheduleCrawler(config)

    date = "2024-01-01"
    result1 = crawler.fetch_schedule(date)
    assert (cache_dir / f"{date}.json").exists()

    # modify cache file to ensure second call reads from cache
    cache_file = cache_dir / f"{date}.json"
    cache_file.write_text(cache_file.read_text().replace("Demo Program", "Cached"))

    result2 = crawler.fetch_schedule(date)
    assert result2[0]["title"] == "Cached"
