from fastapi import APIRouter, HTTPException, Response 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db



router = APIRouter(
    prefix="/playlists",
    tags=['playlists']
)

# get all of a user's playlists
@router.get("/{user_id}/playlists")
def get_user_playlists(user_id: int):
    
    with db.engine.begin() as connection:

        # retrieve all playlists for a user
        sql_to_execute = 'SELECT playlist_id, playlist_name FROM playlist WHERE user_id = :user_id'
        playlists = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': user_id}).fetchall()
        if(isEmpty(playlists)):
            response = {'message': 'no playlists found'}
            return JSONResponse(response, status_code= 404)
        playlist_list = [{'playlist_id': p[0], 'playlist_name': p[1]} for p in playlists]
    return JSONResponse(content=playlist_list, status_code=200) # encapsulate responses with HTTP status codes
    

# create a new playlist for a user
@router.post("/{user_id}")
def create_playlist(current_user_id: int, playlist_name: str):
    
    with db.engine.begin() as connection:

        # insert a new playlist into table
        sql_to_execute = 'INSERT INTO playlist (user_id, playlist_name) VALUES (:user_id, :playlist_name) RETURNING playlist_id'
        result = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': current_user_id, 'playlist_name': playlist_name})

        playlist_id = result.scalar()

    return {"created_playlist_id": playlist_id}


# merge two playlists into a new one
@router.post("/{user_id}/merge/{playlist_one}/{playlist_two}")
def merge_playlists(user_id: int, playlist_one: int, playlist_two: int, new_playlist_name: str):

    with db.engine.begin() as connection:

        # validate user
        user_exists_query = """
            SELECT 1
            FROM user_account
            WHERE user_id = :user_id
        """
        user_exists = connection.execute(
            sqlalchemy.text(user_exists_query),
            {'user_id': user_id}
        ).fetchone()

        if not user_exists:
            return {"error": "User ID does not exist"}, 404

        # validate that playlist_one exists
        playlist_one_query = """
            SELECT 1
            FROM playlist
            WHERE playlist_id = :playlist_one 
        """
        playlist_one_exists = connection.execute(
            sqlalchemy.text(playlist_one_query),
            {'playlist_one': playlist_one}
        ).fetchone()

        if not playlist_one_exists:
            return {"error": f"Playlist {playlist_one} does not exist"}, 404

        # validate that playlist_two exists
        playlist_two_query = """
            SELECT 1
            FROM playlist
            WHERE playlist_id = :playlist_two 
        """
        playlist_two_exists = connection.execute(
            sqlalchemy.text(playlist_two_query),
            {'playlist_two': playlist_two}
        ).fetchone()

        if not playlist_two_exists:
            return {"error": f"Playlist {playlist_two} does not exist"}, 404


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
                        WHERE playlist_id IN (:playlist_one, :playlist_two)
        """
        result = connection.execute(
            sqlalchemy.text(get_songs_sql),
            {'playlist_one': playlist_one, 'playlist_two': playlist_two}
        ).mappings()

        song_ids = [row['song_id'] for row in result]

        # Step 6: Insert each unique song into the new playlist
        insert_data = [{"song_id": song_id, "playlist_id": new_playlist_id} for song_id in song_ids]
        if insert_data:
            add_song_sql = """
                        INSERT INTO playlist_song (song_id, playlist_id)
                        VALUES (:song_id, :playlist_id)
                    """
            connection.execute(sqlalchemy.text(add_song_sql), insert_data)

    return {"new_playlist_id": new_playlist_id, "message": "Playlists merged"}


# delete a playlist belonging to the current user
@router.delete("/{user_id}/playlist/{playlist_id}/delete")
def delete_playlist(current_user_id: int, playlist_id: int):
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
        result = connection.execute(sqlalchemy.text(check_sql), {'playlist_id': playlist_id, 'user_id': current_user_id}).scalar()

        if not result:
            raise HTTPException(status_code=404, detail="Playlist not found or does not belong to the user")

        # Delete the playlist
        delete_sql = "DELETE FROM playlist WHERE playlist_id = :playlist_id"
        connection.execute(sqlalchemy.text(delete_sql), {'playlist_id': playlist_id})

    return Response(status_code=204) # use 204 to signal No Content for success without a body


# view a playlist's songs
@router.get("/{playlist_id}/songs")
def get_songs(playlist_id: int):
    with db.engine.begin() as connection:
        sql_query = sqlalchemy.text("""
        SELECT playlist_name
        FROM playlist
        WHERE playlist_id = :playlist_id
        """)
        sql_dict = {
            'playlist_id': playlist_id
        }
        songs = connection.execute(sql_query, sql_dict).fetchall()
    playlist = []
    for i, song in enumerate(songs[0]):
        playlist.append({
            str(i + 1): song
        })
    if(isEmpty(playlist)):
        return JSONResponse({"message": "playlist is empty"}, status_code=200)
    return JSONResponse(playlist, status_code=200)



# add a song to a playlist (only allowed by playlist creator or a collaborator)
@router.post("/{user_id}/playlist/{playlist}/songs/{song_id}")
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
        print(current_user_id, song_id, playlist_id)
        sql_to_execute = 'INSERT INTO playlist_song (song_id, playlist_id) VALUES (:song_id, :playlist_id)'
        connection.execute(sqlalchemy.text(sql_to_execute), {'song_id': song_id, 'playlist_id': playlist_id})
        response = {'message': 'Playlist added successfully'}
        return JSONResponse(response, status_code=200)


# remove a song from a playlist (only allowed by playlist creator or a collaborator)
@router.delete("/{user_id}/playlist/{playlist_id}/songs/{song_id}")
def delete_song_from_playlist(current_user_id: int, song_id: int, playlist_id: int):
    with db.engine.begin() as connection:
        sql_dict = {
           'user_id': current_user_id,
           'song_id': song_id,
           'playlist_id': playlist_id
        }
        sql_query_exists = sqlalchemy.text("""
            SELECT 1
            FROM playlist_song
            WHERE playlist_song.playlist_id = :playlist_id AND playlist_song.song_id = :song_id
            """)
        exists = connection.execute(sql_query_exists, sql_dict).fetchone()
        if(not(exists)):
            response = {"message": "Song does not exist"}
            return JSONResponse(response, status_code=404)
        
        sql_query_permission = sqlalchemy.text("""
            SELECT 1
            FROM playlist
            JOIN playlist_song ON playlist_song.playlist_id = playlist.playlist_id
            WHERE user_id = :user_id AND playlist.playlist_id = :playlist_id AND song_id = :song_id
            """)
        has_permission = connection.execute(sql_query_permission, sql_dict).fetchone()
        if(not(has_permission)):
            response = {"message": "You must own the playlist to delete a song"}
            return JSONResponse(response, status_code=403)

        sql_query = sqlalchemy.text("""
        DELETE FROM playlist_song
        WHERE playlist_id = :playlist_id AND song_id = :song_id AND 
        (:user_id = (SELECT user_id
                    FROM playlist
                    WHERE playlist_id = :playlist_id) 
        OR :user_id = (SELECT user_id 
                    FROM playlist_collaborator
                    WHERE playlist_id = :playlist_id))
        """)
        connection.execute(sql_query, sql_dict)
    response = {"message": "Song successfully deleted"}
    return JSONResponse(response, status_code=200)

# follow playlist
@router.post("/{user_id}/playlist/{playlist_id}")
def follow_playlist(current_user_id: int, playlist_id: int):
    with db.engine.begin() as connection:
        sql_dict = {
            'user_id': current_user_id,
            'playlist_id': playlist_id
        }

        #check if already followed
        sql_query_getname = sqlalchemy.text("""
            SELECT playlist.playlist_name
            FROM playlist_follower
            JOIN playlist ON playlist.playlist_id = playlist_follower.playlist_id
            WHERE playlist_follower.user_id = :user_id AND playlist_follower.playlist_id = :playlist_id
            """)
        playlist_name = connection.execute(sql_query_getname, sql_dict).fetchone()
        if(playlist_name):
            response = {"message": f"Error: You already follow {playlist_name[0]}"}
            return JSONResponse(response, status_code=409)
        
        #check if the playlist is owned by the user
        sql_query_checkifowner = sqlalchemy.text("""
            SELECT 1
            FROM playlist
            WHERE playlist_id = :playlist_id AND user_id = :user_id
            """)
        sql_query_getname = sqlalchemy.text("""
            SELECT playlist.playlist_name
            FROM playlist
            WHERE playlist.user_id = :user_id AND playlist.playlist_id = :playlist_id
            """)
        isOwner = connection.execute(sql_query_checkifowner, sql_dict).fetchone()
        playlist_name = connection.execute(sql_query_getname, sql_dict).fetchone()
        if(isOwner):
            response = {"message": f"Error: Cannot follow {playlist_name[0]} as you created it."}
            return JSONResponse(response, status_code=409)

        #insert new column with user now following playlist
        sql_query_insert = sqlalchemy.text("""
            INSERT INTO playlist_follower (user_id, playlist_id)
            VALUES (:user_id, :playlist_id)
            """)
        connection.execute(sql_query_insert, sql_dict)

        playlist_name = connection.execute(sql_query_getname, sql_dict).fetchone()
    response = {"message": f"You are now following {playlist_name[0]}"}
    return JSONResponse(response, status_code=201)



# view my playlists (including the ones you're following)/view the playlists of any specific user

# view all playlists (LIMIT 100)

# get song information (pass id in, returns song information)

def isEmpty(argument):
    if(argument):
        return(False)
    return(True)