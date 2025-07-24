from fastapi import FastAPI

app = FastAPI()

@app.get("/status")
def status():
    return {"status": "ok", "message": "Gateway up. Implement RPC calls here."}
