from fastapi import FastAPI

app = FastAPI()

@app.post("/validate")
def validate(data: dict):
    return {"status": "ok", "data": data}

@app.post("/pseudonymize")
def pseudonymize(data: dict):
    return {"token": "abc123", "age_group": "50-59"}

@app.post("/policy")
def policy(data: dict):
    return {"allowed": True}

@app.post("/fairness-check")
def fairness(data: dict):
    return {"risk": "low"}