import asyncio
import time
import aiohttp
from typing import Dict, Any

API_URL = "https://api.llama.fi/chains"   # devuelve TVL actual por cadena

async def fetch_tvl(session: aiohttp.ClientSession, chain: str = "Ethereum") -> Dict[str, Any]:
    async with session.get(API_URL, timeout=20) as resp:
        resp.raise_for_status()
        data = await resp.json()

    # Data es una lista de dicts; filtramos la cadena deseada
    entry = next((d for d in data if d["name"] == chain), None)
    if entry is None:
        raise ValueError(f"Chain {chain} not found in DeFiLlama response")

    return {
        "source": "defillama",
        "chain": chain,
        "timestamp": time.time(),
        "tvl_usd": float(entry["tvl"])
    }


async def run(queue, interval: int = 3600, chain: str = "Ethereum"):
    """
    Lanza una petición cada `interval` segundos y pone dict en la cola.
    """
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                item = await fetch_tvl(session, chain)
                queue.put_nowait(item)
                print(f"[defillama] pushed TVL {item['tvl_usd']:.0f} USD")
            except Exception as e:
                print(f"[defillama] error: {e}")
            await asyncio.sleep(interval)
