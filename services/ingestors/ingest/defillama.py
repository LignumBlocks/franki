# services/ingestors/ingest/defillama.py
import aiohttp
import pandas as pd
from .base import Ingestor

API_URL = "https://api.llama.fi/chains"

class DefiLlamaIngestor(Ingestor):
    def __init__(self, chain="Ethereum"):
        self.chain = chain

    async def fetch(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(API_URL, timeout=15) as resp:
                resp.raise_for_status()
                data = await resp.json()

        for entry in data:
            if entry["name"] == self.chain:
                return {
                    "chain": self.chain,
                    "tvl_usd": float(entry["tvl"]),
                    "timestamp": self.now,
                    "source": "defillama"
                }

        raise ValueError(f"Chain {self.chain} not found in DeFiLlama")

    def transform(self, raw) -> pd.DataFrame:
        return pd.DataFrame([raw])
