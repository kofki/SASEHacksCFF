# routes/scans.py
from fastapi import APIRouter

scans_router = APIRouter()

@scans_router.get("/")
def list_scans():
    return []

@scans_router.get("/{scan_id}")
def get_scan(scan_id: str):
    return {}

@scans_router.post("/")
def create_scan():
    return {}