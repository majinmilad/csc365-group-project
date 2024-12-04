from fastapi import APIRouter, HTTPException, Response 
from fastapi.responses import JSONResponse
import sqlalchemy
from src import database as db

router = APIRouter(
    prefix="/analytics",
    tags=['analytics']
)

#will end up being the two complex endpoints

@router.get("/playlists")
def most_popular_playlists():
    with db.engine.begin() as connection:
        sql_query = sqlalchemy.text("""
            SELECT playlist.playlist_id as id, playlist.playlist_name as name, COUNT(playlist_follower.playlist_id)
            FROM playlist_follower
            JOIN playlist ON playlist.playlist_id = playlist_follower.playlist_id
            GROUP BY playlist.playlist_id, playlist.playlist_name
            ORDER BY count DESC
            LIMIT 100
        """)
        playlists = connection.execute(sql_query).fetchall()
        results = []
        for i, playlist in enumerate(playlists):
            results.append({
                "popularity": i + 1,
                "name": playlist.name,
                "id": playlist.id
            })
    return results
    


@router.get("/songs")
def most_popular_songs():
    with db.engine.begin() as connection:
        sql_query = sqlalchemy.text("""
            WITH Ranked_songs AS
            (
                SELECT song.song_id as id, song.title, album.title as album_name, artist.name as artist_name, playlist_song.playlist_id, COUNT(playlist_song.playlist_id) OVER (PARTITION BY song.song_id) AS saves
                FROM song
                LEFT JOIN playlist_song ON playlist_song.song_id = song.song_id
                JOIN album ON album.album_id = song.album_id
                JOIN artist ON artist.artist_id = song.artist_id
                LIMIT 100
            ),
            Distinct_songs AS
            (
                SELECT DISTINCT Saves, Ranked_songs.title, album_name, artist_name, id
                FROM Ranked_Songs
            )
            SELECT RANK() OVER (ORDER BY saves DESC, title ASC) AS Rnk, title, album_name, artist_name, id
            FROM Distinct_songs
            """)
        songs = connection.execute(sql_query).fetchall()
        print(songs)
        results = []
        for i, song in enumerate(songs):
            results.append({
                "popularity": i + 1,
                "name": song.title,
                "album": song.album_name,
                "artist": song.artist_name,
                "id": song.id
            })
    return results