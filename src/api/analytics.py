from fastapi import APIRouter, HTTPException, Response 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/analytics",
    tags=['analytics']
)

#will end up being the two complex endpoints

@router.get("/user/{user_id}/playlists")
def find_recommended_playlists(user_id: int):
    return

@router.get("/user/{user_id}/collaborator")
def find_collaborators(user_id: int):
    return