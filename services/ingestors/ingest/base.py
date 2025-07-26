# services/ingestors/ingest/base.py
from abc import ABC, abstractmethod
from datetime import datetime
import pandas as pd

class Ingestor(ABC):
    @abstractmethod
    async def fetch(self):
        """
        Devuelve los datos crudos (dicts, lista de dicts, etc.)
        """
        pass

    @abstractmethod
    def transform(self, raw) -> pd.DataFrame:
        """
        Convierte los datos crudos en un DataFrame limpio
        """
        pass

    @property
    def now(self) -> int:
        """Timestamp actual en milisegundos (UTC)"""
        return int(datetime.utcnow().timestamp() * 1000)
