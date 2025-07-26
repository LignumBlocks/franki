import asyncio
from ingest.defillama import DefiLlamaIngestor
from utils.storage import dump_parquet

async def run_ingestor(ingestor, interval=3600):
    while True:
        try:
            raw = await ingestor.fetch()
            df = ingestor.transform(raw)
            dump_parquet(df, source=raw["source"])  # pasa DataFrame y nombre
            print(f"[{raw['source']}] {raw}")
        except Exception as e:
            print(f"[{type(ingestor).__name__}] error → {e}")
        await asyncio.sleep(interval)

async def main():
    ingestores = [
        DefiLlamaIngestor(chain="Ethereum"),
        # más ingestores aquí
    ]
    await asyncio.gather(*(run_ingestor(i) for i in ingestores))

if __name__ == "__main__":
    asyncio.run(main())
