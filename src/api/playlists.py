from fastapi import APIRouter, Depends, HTTPException, Request, Response 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db
from typing import Optional, List

router = APIRouter(
    prefix="/playlists",
    tags=['playlists']
)

# create a new playlist for a user
@router.post("/{user_id}/playlist/create_playlist")
def create_playlist(current_user_id: int, playlist_name: str):
    
    with db.engine.begin() as connection:

        # insert a new playlist into table
        sql_to_execute = 'INSERT INTO playlist (user_id, playlist_name) VALUES (:user_id, :playlist_name) RETURNING playlist_id'
        result = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': current_user_id, 'playlist_name': playlist_name})

        playlist_id = result.scalar()

    return playlist_id

# delete a playlist belonging to the current user
@router.delete("/{user_id}/playlist/{playlist_id}/delete")
def delete_playlist(user_id: int, playlist_id: int):
    """
    Deletes a playlist by its ID if it belongs to the given user
    """
    with db.engine.begin() as connection:

        # check if the playlist exists and belongs to the user
        check_sql = """
                    SELECT 1
                    FROM playlist
                    WHERE playlist_id = :playlist_id AND user_id = :user_id
                    """
        result = connection.execute(sqlalchemy.text(check_sql), {'playlist_id': playlist_id, 'user_id': user_id}).scalar()

        if not result:
            raise HTTPException(status_code=404, detail="Playlist not found or does not belong to the user")

        # Delete the playlist
        delete_sql = "DELETE FROM playlist WHERE playlist_id = :playlist_id"
        connection.execute(sqlalchemy.text(delete_sql), {'playlist_id': playlist_id})

    return Response(status_code=204) # use 204 to signal No Content for success without a body

# get all of a user's playlists
@router.get("/{user_id}/playlists")
def get_user_playlists(user_id: int):
    
    with db.engine.begin() as connection:

        # retrieve all playlists for a user
        sql_to_execute = 'SELECT playlist_id, playlist_name FROM playlist WHERE user_id = :user_id'
        playlists = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': user_id})
        playlist_list = [{'playlist_id': p[0], 'playlist_name': p[1]} for p in playlists]
        return JSONResponse(content=playlist_list, status_code=200) # encapsulate responses with HTTP status codes

# add a song to a playlist belonging to the user
@router.post("/{user_id}/playlist/add_song")
def add_song_to_playlist(current_user_id: int, song_id: int, playlist_id: int):

    with db.engine.begin() as connection:

        # validate user
        user_exists = connection.execute(sqlalchemy.text(
            "SELECT 1 FROM user_account WHERE user_id = :user_id"
        ), {'user_id': current_user_id}).fetchone()

        # validate song
        song_exists = connection.execute(sqlalchemy.text(
            "SELECT 1 FROM song WHERE song_id = :song_id"
        ), {'song_id': song_id}).fetchone()

        # validate playlist
        playlist_exists = connection.execute(sqlalchemy.text(
            "SELECT 1 FROM playlist WHERE playlist_id = :playlist_id"
        ), {'playlist_id': playlist_id}).fetchone()

        # validate user has playlist modification auth
        user_allowed = connection.execute(sqlalchemy.text(
        """SELECT 1
            FROM public.playlist
            WHERE playlist_id = :playlist_id AND user_id = :user_id
            OR EXISTS (
            SELECT 1 
            FROM public.playlist_collaborator 
            WHERE playlist_id = :playlist_id AND user_id = :user_id)"""
        ), {'user_id': current_user_id, 'playlist_id': playlist_id}).fetchone()

        # check
        if not user_exists or not playlist_exists or not song_exists or not user_allowed:
            return {"ERROR": "Invalid user_id, song_id or playlist_id"}, 400

        # insert a new playlist into table
        sql_to_execute = 'INSERT INTO playlist_song (song_id, playlist_id) VALUES (:song_id, :playlist_id)'
        connection.execute(sqlalchemy.text(sql_to_execute), {'song_id': song_id, 'playlist_id': playlist_id})
    
        return Response(status_code=204) # use 204 to signal No Content for success without a body

# remove song

# change playlist name

# follow playlist

# view a playlist's songs

# view my playlists (including the ones you're following)

# view the playlists of any specific user

# view all playlists (LIMIT 100)


# merge two playlists into a new one




# basically a name updater but havent checked it vvv
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
