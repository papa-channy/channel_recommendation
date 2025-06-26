import pandas as pd
from pathlib import Path
from typing import Any
from src.domain.interfaces import DataLoaderInterface

class FileDataLoader(DataLoaderInterface):
    def __init__(self, config: dict):
        self.path = Path(config['paths']['movielens'])

    def get_processed_movielens_data(self) -> pd.DataFrame:
        if self.path.suffix == '.parquet':
            return pd.read_parquet(self.path)
        return pd.read_csv(self.path)
