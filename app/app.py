from fastapi import FastAPI, HTTPException

app = FastAPI(title="Subscription Notification Service", version="0.0.1")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/notifications")
def list_notifications():
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

@app.post("/notifications")
def create_notification(payload: dict):
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

@app.put("/notifications")
def replace_notifications():
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

@app.delete("/notifications")
def delete_notifications():
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")