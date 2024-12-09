from fastapi import APIRouter, Response 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db



router = APIRouter(
    prefix="/playlists",
    tags=['playlists']
)

#get all playlists
@router.get("/all")
def Get_playlist_catalog():

    with db.engine.begin() as connection:

        # get first 100 rows of playlists
        sql_query = sqlalchemy.text("""
            SELECT playlist_id, playlist_name
            FROM playlist
            LIMIT 100
        """)
        playlists = connection.execute(sql_query).fetchall()

    # no playlists to return
    if not playlists:
        return JSONResponse({"Error": "No playlists available."}, status_code=404)

    # build list of playlists
    playlist_list = [
        {"playlist_id": row.playlist_id, "playlist_name": row.playlist_name}
        for row in playlists
    ]

    return JSONResponse(content=playlist_list, status_code=200)

@router.get("/{user_id}/all-playlists")
def Get_user_followed_and_created_playlists(user_id: int):

    with db.engine.begin() as connection:

        # get all playlists created by user (owner as role)
        # get all playlists followed by user (follower as role)
        sql_query = """
            SELECT playlist.playlist_id, playlist.playlist_name, 'owner' as role
            FROM playlist
            WHERE playlist.user_id = :user_id
            UNION
            SELECT playlist.playlist_id, playlist.playlist_name, 'follower' as role
            FROM playlist_follower
            JOIN playlist ON playlist.playlist_id = playlist_follower.playlist_id
            WHERE playlist_follower.user_id = :user_id
        """
        playlists = connection.execute(sqlalchemy.text(sql_query),
                                       {'user_id': user_id}).fetchall()

    # nothing returned-- user DNE or no user does not follow/ own playlists
    if not playlists:
        return JSONResponse({"message": "No playlists found for this user."}, status_code=404)

    # build list of playlists
    playlist_list = [
        {"playlist_id": row.playlist_id, "playlist_name": row.playlist_name, "role": row[2]}
        for row in playlists
    ]

    return JSONResponse(content=playlist_list, status_code=200)

# get all of a user's playlists
@router.get("/{user_id}/playlists")
def get_user_created_playlists(user_id: int):
    
    with db.engine.begin() as connection:

        # retrieve all playlists for a user
        sql_to_execute = 'SELECT playlist_id, playlist_name FROM playlist WHERE user_id = :user_id'
        playlists = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': user_id}).fetchall()
        if(isEmpty(playlists)):
            
            return JSONResponse({'message': 'no playlists found'}, status_code= 404)
        playlist_list = [{'playlist_id': p.playlist_id, 'playlist_name': p.playlist_name} for p in playlists]
    return JSONResponse(content=playlist_list, status_code=200) # encapsulate responses with HTTP status codes
    

# create a new playlist for a user
@router.post("/{user_id}")
def create_playlist(current_user_id: int, playlist_name: str):
    
    with db.engine.begin() as connection:
        sql_user_exists = sqlalchemy.text("""
            SELECT 1
            FROM user_account
            WHERE user_id = :user_id
            """)
        exists = connection.execute(sql_user_exists, {'user_id': current_user_id}).fetchone()
        print(exists)
        if(not(exists)):
            return JSONResponse({"Error": "User does not exist"}, status_code=404)
        
        # insert a new playlist into table
        sql_to_execute = 'INSERT INTO playlist (user_id, playlist_name) VALUES (:user_id, :playlist_name) RETURNING playlist_id'
        result = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': current_user_id, 'playlist_name': playlist_name})

        playlist_id = result.scalar()

    return JSONResponse({"created_playlist_id": playlist_id}, status_code=201)


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
            return JSONResponse({"Error": "User ID does not exist"}, status_code= 404)

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
            return JSONResponse({"Error": f"Playlist {playlist_one} does not exist"}, status_code= 404)

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
            return JSONResponse({"Error": f"Playlist {playlist_two} does not exist"}, status_code= 404)


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

    return JSONResponse({"new_merged_playlist_id": new_playlist_id}, status_code= 201)


# delete a playlist belonging to the current user
@router.delete("/{user_id}/playlist/{playlist_id}")
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
        result = connection.execute(sqlalchemy.text(check_sql), {'playlist_id': playlist_id, 'user_id': current_user_id}).fetchone()
        print(current_user_id, playlist_id)
        print(result)

        if not result:
            return JSONResponse({'Error':"Playlist not found or does not belong to the user"}, status_code= 404)

        # Delete the playlist
        delete_sql = "DELETE FROM playlist WHERE playlist_id = :playlist_id"
        connection.execute(sqlalchemy.text(delete_sql), {'playlist_id': playlist_id})

    return Response(status_code=204) # use 204 to signal No Content for success without a body


# view a playlist's songs
@router.get("/{playlist_id}/songs")
def get_songs(playlist_id: int):
    with db.engine.begin() as connection:
        sql_check = sqlalchemy.text("""
            SELECT 1
            FROM playlist
            WHERE playlist_id = :playlist_id
        """)

        sql_query_songs = sqlalchemy.text("""
            SELECT song.song_id as id, song.title as song_name
            FROM playlist_song
            JOIN song ON playlist_song.song_id = song.song_id
            WHERE playlist_song.playlist_id = :playlist_id
        """)
        sql_query_playlist = sqlalchemy.text("""
            SELECT playlist_name
            FROM playlist
            WHERE playlist.playlist_id = :playlist_id

        """)
        sql_query_user = sqlalchemy.text("""
            SELECT concat(first_name, ' ', last_name) AS name
            FROM playlist
            JOIN user_account ON user_account.user_id = playlist.user_id
            WHERE playlist.playlist_id = :playlist_id
        """)
        sql_dict = {
            'playlist_id': playlist_id
        }
        exists = connection.execute(sql_check, sql_dict).fetchone()
        if(not(exists)):
            return JSONResponse({"Error": "Playlist does not exist"}, 404)
        
        songs = connection.execute(sql_query_songs, sql_dict).fetchall()
        playlist_name = connection.execute(sql_query_playlist, sql_dict).fetchone()
        owner_name = connection.execute(sql_query_user, sql_dict).fetchone()

    track_list = []
    for i, song in enumerate(songs):
        track_list.append({
            "id": song.id,
            "name": song.song_name
        })

    playlist = {
        'name': playlist_name.playlist_name,
        'created_by': owner_name.name, 
        'tracks': track_list
    }
    return playlist

#get song information
@router.get("/songs/{song_id}")
def get_song_information(song_id: int):

    with db.engine.begin() as connection:

        # get song info for a song id
        sql_query = """
            SELECT song_id, song.title as song_name, artist.name as artist_name, album.title as album_name, duration
            FROM song
            JOIN artist ON artist.artist_id = song.artist_id
            JOIN album ON album.album_id = song.album_id
            WHERE song_id = :song_id
        """
        song_info = connection.execute(sqlalchemy.text(sql_query), {'song_id': song_id}).fetchone()

    # song DNE in song table
    if not song_info:
        return JSONResponse({"message": "Song not found."}, status_code=404)


    # format song information
    song_data = {
        "id": song_info.song_id,
        "title": song_info.song_name,
        "artist": song_info.artist_name,
        "album": song_info.album_name,
        "song_duration": f"{song_info.duration}s"
    }

    return JSONResponse(content=song_data, status_code=200)


# add a song to a playlist (only allowed by playlist creator or a collaborator)
@router.post("/{playlist}/songs/{song_id}")
def add_song_to_playlist(current_user_id: int, playlist_id: int, song_id: int):

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
            return JSONResponse({"ERROR": "Invalid user_id, song_id or playlist_id"}, status_code= 400)

        # insert a new playlist into table
        print(current_user_id, song_id, playlist_id)
        sql_to_execute = 'INSERT INTO playlist_song (song_id, playlist_id) VALUES (:song_id, :playlist_id)'
        connection.execute(sqlalchemy.text(sql_to_execute), {'song_id': song_id, 'playlist_id': playlist_id})
        return Response(status_code=204)


# remove a song from a playlist (only allowed by playlist creator or a collaborator)
@router.delete("/{playlist_id}/songs/{song_id}")
def delete_song_from_playlist(current_user_id: int, playlist_id: int, song_id: int):
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
            return JSONResponse({"message": "Song does not exist"}, status_code=404)
        
        sql_query_permission = sqlalchemy.text("""
            SELECT 1
            FROM playlist
            WHERE (:user_id = (SELECT user_id
                FROM playlist
                WHERE playlist_id = :playlist_id) 
                OR :user_id = (SELECT user_id 
                FROM playlist_collaborator
                WHERE playlist_id = :playlist_id))
            """)
        has_permission = connection.execute(sql_query_permission, sql_dict).fetchone()
        if(not(has_permission)):
            return JSONResponse({"message": "Only owners/collaborators may delete a song"}, status_code=403)

        sql_query = sqlalchemy.text("""
        DELETE FROM playlist_song
        WHERE playlist_id = :playlist_id AND song_id = :song_id
        """)
        connection.execute(sql_query, sql_dict)
    return Response(status_code=204)

# follow playlist
@router.post("/{user_id}/playlist/{playlist_id}/follow")
def follow_playlist(current_user_id: int, playlist_id: int):
    with db.engine.begin() as connection:
        sql_dict = {
            'user_id': current_user_id,
            'playlist_id': playlist_id
        }

        #check if already followed
        sql_query_getname = sqlalchemy.text("""
            SELECT playlist.playlist_name as p_name
            FROM playlist_follower
            JOIN playlist ON playlist.playlist_id = playlist_follower.playlist_id
            WHERE playlist_follower.user_id = :user_id AND playlist_follower.playlist_id = :playlist_id
            """)
        playlist_name = connection.execute(sql_query_getname, sql_dict).fetchone()
        if(playlist_name):
            response = {"Error": f"You already follow {playlist_name.p_name}"}
            return JSONResponse(response, status_code=409)
        
        #check if the playlist is owned by the user
        sql_query_checkifowner = sqlalchemy.text("""
            SELECT 1
            FROM playlist
            WHERE playlist_id = :playlist_id AND user_id = :user_id
            """)
        sql_query_getname_if_owner = sqlalchemy.text("""
            SELECT playlist.playlist_name as p_name
            FROM playlist
            WHERE playlist.user_id = :user_id AND playlist.playlist_id = :playlist_id
            """)
        isOwner = connection.execute(sql_query_checkifowner, sql_dict).fetchone()
        playlist_name = connection.execute(sql_query_getname_if_owner, sql_dict).fetchone()
        if(isOwner):
            response = {"Error": f"Cannot follow {playlist_name.p_name} as you created it."}
            return JSONResponse(response, status_code=409)

        #insert new column with user now following playlist
        sql_query_insert = sqlalchemy.text("""
            INSERT INTO playlist_follower (user_id, playlist_id)
            VALUES (:user_id, :playlist_id)
            """)
        connection.execute(sql_query_insert, sql_dict)

        playlist_name = connection.execute(sql_query_getname, sql_dict).fetchone()
    response = {"Success": f"You are now following {playlist_name.p_name}"}
    return JSONResponse(response, status_code=201)


#unfollow a playlist assuming it exists
#on a ui you would only be able to unfollow playlist you exist
@router.delete("/{user_id}/playlist/{playlist}/unfollow")
def unfollow_playlist(current_user_id: int, playlist_id: int):
    with db.engine.begin() as connection:
        sql_dict = {
            'user_id': current_user_id,
            'playlist_id': playlist_id
        }

        sql_query_check = sqlalchemy.text("""
            SELECT 1
            FROM playlist_follower
            WHERE playlist_follower.user_id = :user_id AND playlist_follower.playlist_id = :playlist_id
            """)
        follows = connection.execute(sql_query_check, sql_dict).fetchone()

        sql_query_getname = sqlalchemy.text("""
            SELECT playlist_name as p_name
            FROM playlist
            WHERE playlist_id = :playlist_id
            """)
        playlist_name = connection.execute(sql_query_getname, sql_dict).fetchone()
        if(not(follows)):
            return JSONResponse({"Error": f"You don't follow {playlist_name.p_name}"}, status_code=400)
            
        sql_query = sqlalchemy.text("""
        DELETE FROM playlist_follower
        WHERE playlist_id = :playlist_id AND user_id = :user_id
        """)
        connection.execute(sql_query, sql_dict)
        return JSONResponse({"Success": f"You unfollowed {playlist_name.p_name}"}, status_code=200)

def isEmpty(argument):
    if(argument):
        return(False)
    return(True)