from abc import ABC, abstractmethod
import pandas as pd

class DataLoaderInterface(ABC):
    @abstractmethod
    def get_processed_movielens_data(self) -> pd.DataFrame:
        """Load preprocessed MovieLens data."""
        raise NotImplementedError
