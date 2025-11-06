from src.AquaKeeper import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"ok": True, "msg": "Hello from Render + FastAPI!"}
