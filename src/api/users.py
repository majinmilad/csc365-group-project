from fastapi import APIRouter, Depends, Request 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db
from typing import Optional, List
import json

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


@router.post("/{user_id}/playlist/create_playlist")
def create_playlist(user_id: int, playlist_name: str = None):
    
    with db.engine.begin() as connection:

        # insert a new playlist into table
        sql_to_execute = 'INSERT INTO playlist (user_id) VALUES (:user_id) RETURNING playlist_id'
        result = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': user_id})

        playlist_id = result.scalar()

        # update the playlist with a name if one was provided
        if playlist_name is not None:
            sql_to_execute = 'UPDATE playlist SET playlist_name = :playlist_name WHERE playlist_id = :playlist_id'
            connection.execute(sqlalchemy.text(sql_to_execute), {'playlist_name': playlist_name, 'playlist_id': playlist_id})

    return playlist_id


@router.post("/{user_id}/playlist/add_song")
def add_song_to_playlist(user_id: int, song_id: int, playlist_id: int):

    with db.engine.begin() as connection:

        # validate user
        user_exists = connection.execute(sqlalchemy.text(
            "SELECT 1 FROM user WHERE user_id = :user_id"
        ), {'user_id': user_id}).fetchone()

        # validate playlist
        playlist_exists = connection.execute(sqlalchemy.text(
            "SELECT 1 FROM playlist WHERE playlist_id = :playlist_id"
        ), {'playlist_id': playlist_id}).fetchone()

        # check
        if not user_exists or not playlist_exists:
            return {"error": "Invalid user_id or playlist_id"}, 400

        # insert a new playlist into table
        sql_to_execute = 'INSERT INTO playlist_song (song_id, playlist_id) VALUES (:song_id, :playlist_id)'
        connection.execute(sqlalchemy.text(sql_to_execute), {'song_id': song_id, 'playlist_id': playlist_id})
    
    return "Ok"


@router.get("/{user_id}/playlists")
def get_user_playlists(user_id: int):
    with db.engine.begin() as connection:

        # retrieve all playlists for a user
        sql_to_execute = 'SELECT playlist_id, playlist_name FROM playlist WHERE user_id = :user_id'
        playlists = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': user_id})
        playlist_list = [{'playlist_id': p[0], 'playlist_name': p[1]} for p in playlists]
        return JSONResponse(content=playlist_list, status_code=200) # encapsulate responses with HTTP status codes

@router.get("/{user_id}/playlists/{id}")
def get_a_playlist(user_id: int, playlist_id: int):
    with db.engine.begin() as connection:

        # retrieve all playlists for a user
        sql_to_execute = 'SELECT playlist_id, playlist_name FROM playlist WHERE user_id = :user_id AND playlist_id = :playlist_id'
        playlists = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': user_id, 'playlist_id': playlist_id})
        playlist_list = []
        for playlist in playlists:
            playlist_list.append({'playlist_id': playlist[0], 'playlist_name': playlist[1]})
    return playlist_list

@router.post("/{user_id}/playlists/merge")
def merge_playlists(user_id: int, playlist_ids: List[int], new_playlist_name: str):

    with db.engine.begin() as connection:

        # make empty playlist to store merged playlist in
        make_playlist_sql = """  
                            INSERT INTO playlist (user_id, playlist_name)
                            VALUES (:user_id, :playlist_name)
                            RETURNING playlist_id
                            """
        new_playlist_result = connection.execute(
            sqlalchemy.text(make_playlist_sql),
            {'user_id': user_id, 'playlist_name': new_playlist_name}
        )
        new_playlist_id = new_playlist_result.scalar()

        # get all songs ids to put into a playlist
        get_songs_sql = """
                        SELECT DISTINCT song_id
                        FROM playlist_song
                        WHERE playlist_id = ANY(:playlist_ids)
                        """
        result = connection.execute(sqlalchemy.text(get_songs_sql), {'playlist_ids': playlist_ids})
        song_ids = [row['song_id'] for row in result]

        # batch insert each unique song into the new playlist
        insert_data = [{"song_id": song_id, "new_playlist_id": new_playlist_id} for song_id in song_ids]
        if insert_data:
            add_song_sql = 'INSERT INTO playlist_song (song_id, playlist_id) VALUES (:song_id, :new_playlist_id)'
            connection.execute(sqlalchemy.text(add_song_sql), insert_data)

    return {"new_playlist_id": new_playlist_id, "message": "Playlists merged"}


@router.patch("/{user_id}/playlists/{playlist_id}/update")
def update_playlist(user_id: int, playlist_id: int, new_name: Optional[str] = None):

    with db.engine.begin() as connection:

        # update playlist name-- if it belongs to the user
        sql_to_execute = """
                         UPDATE playlist SET playlist_name = :new_name 
                         WHERE playlist_id = :playlist_id 
                         AND user_id = :user_id
                         """
        result = connection.execute(
            sqlalchemy.text(sql_to_execute),
            {'new_name': new_name, 'playlist_id': playlist_id, 'user_id': user_id}
        )

        # check if row was updated
        if result.rowcount == 0:
            return {"error": "Playlist not found or not owned by the user"}, 404

    return {"message": "Playlist updated"}


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
