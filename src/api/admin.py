from fastapi import APIRouter, HTTPException, Response 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db
from .search import search_for_songs
import spotify_auth
import requests
import json


router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

#targets
#could update song search to use strings, but not sure
#recommend songs/albums/artists
#recommend people

#add songs by searching them
@router.get("/song/{name}/{album}/{artist}")
def search_for_songs(song_name: str = '', album_name: str = '', artist_name: str = ''):
    if(isEmpty(song_name) and isEmpty(album_name) and isEmpty(artist_name)):
        return JSONResponse({"Error": "Nothing Entered"}, status_code=400)
    token = spotify_auth.get_spotify_token()
    url = "https://api.spotify.com/v1/search"
    headers = spotify_auth.get_auth_header(token)
    query = f"?q={song_name + ' ' + album_name + ' ' + artist_name}&type=track&limit=1"

    query_url = url + query
    response = requests.get(query_url, headers=headers)
    json_result = json.loads(response.content)
    song_list = []
    for song in json_result['tracks']['items']:
        song_list.append(
            {
                #'id': song['id'],
                'name': song['name'],
                #'type': song['type'],
                #'track': song['track_number'],
                'album': song['album']['name'],
                'artist': song['artists'][0]['name'],
                #'popularity': str(song['popularity']),
                'duration': str(song['duration_ms']//1000) + 's'
            }
        )

    song = song_list
    with db.engine.begin() as connection:
        sql_dict_artist = {
            "artist": song[0]['artist'],
        }
        sql_query_artist = sqlalchemy.text("""
            WITH inserted AS (
                INSERT INTO artist (name)
                VALUES (:artist)
                ON CONFLICT (name) DO NOTHING
                RETURNING artist_id
            )
            SELECT artist_id
            FROM inserted
            UNION ALL
            SELECT artist_id
            FROM artist
            WHERE name = :artist                              
            """)
        artist_id = connection.execute(sql_query_artist, sql_dict_artist).scalar()
        sql_dict_album = {
            "album": song[0]['album'],
            "artist_id": artist_id,
        }
        sql_query_album = sqlalchemy.text("""
            WITH inserted AS (
                INSERT INTO album (title, artist_id)
                VALUES (:album, :artist_id)
                ON CONFLICT (title) DO NOTHING
                RETURNING album_id 
            )
            SELECT album_id
            FROM inserted
            UNION ALL
            SELECT album_id
            FROM album
            WHERE title = :album
            """)
        album_id = connection.execute(sql_query_album, sql_dict_album).scalar()
        sql_dict_song = {
            "song": song[0]['name'],
            "artist_id": artist_id,
            "album_id": album_id,
            "duration": int(song[0]['duration'][0:3])
        }
        sql_query_song = sqlalchemy.text("""
            INSERT INTO song (title, album_id, artist_id, duration)
            VALUES (:song, :album_id, :artist_id, :duration)
            """)
        connection.execute(sql_query_song, sql_dict_song)
    return Response(status_code=204)

def isEmpty(string):
    if(string):
        return False
    return True