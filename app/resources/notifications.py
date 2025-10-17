from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/notifications")
def list_notifications():
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

@router.post("/notifications")
def create_notification(payload: dict):
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

@router.put("/notifications")
def replace_notifications():
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")

@router.delete("/notifications")
def delete_notifications():
    raise HTTPException(status_code=501, detail="NOT IMPLEMENTED")


