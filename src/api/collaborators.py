from fastapi import APIRouter, Depends, Request 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db
from typing import Optional, List

router = APIRouter(
    prefix="/collaborators",
    tags=['collaborators']
)

@router.patch("/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_user_id}")
def add_collaborator(playlist_id: int, collaborator_user_id: int):
    
    with db.engine.begin() as connection:

        # insert record connecting playlist to collaborating user
        make_playlist_sql = """  
                            INSERT INTO playlist_collaborator (playlist_id, user_id)
                            VALUES (:playlist_id, :user_id)
                            """
        connection.execute(sqlalchemy.text(make_playlist_sql), {'playlist_id': playlist_id, 'user_id': collaborator_user_id})
    return 'OK'

@router.delete("/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_user_id}")
def remove_collaborator(playlist_id: int, collaborator_user_id: int):
    
    with db.engine.begin() as connection:

        # insert record connecting playlist to collaborating user
        make_playlist_sql = """  
                            DELETE FROM playlist_collaborator
                            WHERE playlist_id = :playlist_id AND user_id = :user_id
                            """
        connection.execute(sqlalchemy.text(make_playlist_sql), {'playlist_id': playlist_id, 'user_id': collaborator_user_id})
    return 'OK'
