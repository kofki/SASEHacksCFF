# routes/cards.py
from fastapi import APIRouter

cards_router = APIRouter()

@cards_router.get("/")
def list_cards():
    return []

@cards_router.post("/")
def create_card():
    return {}

@cards_router.delete("/{card_id}")
def cancel_card(card_id: str):
    return {"cancelled": True}