from abc import ABC, abstractmethod
import pandas as pd

class PersonaGeneratorInterface(ABC):
    @abstractmethod
    def generate_dummy_watch_history(self, persona_id: str, num_records: int = 20) -> pd.DataFrame:
        """Generate dummy watch history for a persona."""
        raise NotImplementedError
