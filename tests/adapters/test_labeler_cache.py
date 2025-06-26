import os
from src.adapters.gemini_content_labeler import GeminiContentLabeler
from src.infrastructure.cache_manager import CacheManager

def test_labeler_uses_cache(tmp_path, monkeypatch):
    db_path = tmp_path / "cache.db"
    cache = CacheManager(db_path=str(db_path))
    os.environ["GEMINI_API_KEY"] = "dummy"
    labeler = GeminiContentLabeler({"default_labels": ["x"]}, cache)

    labels1 = labeler.generate_labels("t", "o")
    assert labels1 == ["x"]
    # modify cache to verify retrieval
    cache.conn.execute("UPDATE labels_cache SET labels=? WHERE content_hash=?", ("y", "t:o"))
    cache.conn.commit()
    labels2 = labeler.generate_labels("t", "o")
    assert labels2 == ["y"]
