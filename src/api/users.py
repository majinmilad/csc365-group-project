from fastapi import APIRouter, Depends, Request 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db
from typing import Optional, List

# TODO: implement verification that user is either the owner or collaborator of a playlist before allowing edits to be made
# TODO: implement path changes:
# /user/{user_id}/playlist/create_playlist
# Change to POST users/{user_id}/playlists
# /user/{user_id}/playlist/add_song
# Change to POST users/{user_id}/songs
# users/{user_id}/playlists/{playlist_id}/update
# Change to PATCH users/{user_id}/playlists/{playlist_id}/
# /users/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_user_id}
# Change to POST /users/{user_id}/playlists/{playlist_id}/collaborators/{collaborator_user_id}
# /users/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_user_id}
# Change to DELETE /users/{user_id}/playlists/{playlist_id}/collaborators/{collaborator_user_id}


router = APIRouter(
    prefix="/users",
    tags=['users']
)

@router.post("/create")
def create_user(first_name: str, last_name: str):
    with db.engine.begin() as connection:

        # insert new user into users table and retrieve user_id
        sql_to_execute = """
            INSERT INTO user (first_name, last_name) 
            VALUES (:first_name, :last_name) 
            RETURNING user_id
        """
        result = connection.execute(
            sqlalchemy.text(sql_to_execute),
            {'first_name': first_name, 'last_name': last_name}
        )
        return {"user_id": result.scalar()}
