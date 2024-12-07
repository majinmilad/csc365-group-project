from fastapi import APIRouter, Response 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/search",
    tags=['search']
)

@router.get("/playlists/{name}")
def search_for_playlists(playlist_name: str=''):
    with db.engine.begin() as connection:
        sql_dict = {
            'playlist_name': playlist_name
        }
        sql_query = sqlalchemy.text("""
            SELECT playlist.playlist_id as id, playlist_name, COUNT(playlist_follower.user_id) as followers
            FROM playlist
            JOIN playlist_follower ON playlist_follower.playlist_id = playlist.playlist_id
            WHERE playlist_name ILIKE :playlist_name
            GROUP BY id, playlist_name
            ORDER BY followers DESC
            """)
        playlists = connection.execute(sql_query, sql_dict).fetchall()

        results = []
        for playlist in playlists:
            results.append({
                'id': playlist.id,
                'name': playlist.playlist_name,
                'followers': playlist.followers
            })
    return results

@router.get("/songs/{name}")
def search_for_songs(song_name: str = ''):
    with db.engine.begin() as connection:
        sql_dict = {
            'song_name': song_name
        }
        sql_query = sqlalchemy.text("""
            SELECT COALESCE(COUNT(playlist_song.playlist_id), 0) as popularity, song.song_id as id, song.title as song_title, album.title as album_title, artist.name as artist_name, duration
            FROM song
            JOIN album ON album.album_id = song.album_id
            JOIN artist ON artist.artist_id = song.artist_id
            LEFT JOIN playlist_song ON playlist_song.song_id = song.song_id
            WHERE song.title ILIKE :song_name
            GROUP BY song.song_id, song.title, album.title, artist.name, duration
            ORDER BY popularity
            """)
        songs = connection.execute(sql_query, sql_dict).fetchall()
        results = []
        for song in songs:
            results.append({
                'id': song.id,
                'popularity': song.popularity,
                'name': song.song_title,
                'album': song.album_title,
                'artist': song.artist_name,
                'duration': song.duration
            })
    return results