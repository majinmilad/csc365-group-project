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
            CREATE MATERIALIZED VIEW IF NOT EXISTS song_saves AS
            SELECT song_id as id, COUNT(playlist_song.playlist_id) AS saves
            FROM playlist_song
            GROUP BY song_id
            ORDER BY COUNT(playlist_song.playlist_id);

            CREATE INDEX IF NOT EXISTS idx_song_saves ON song_saves(saves);

            SELECT RANK() OVER (ORDER BY saves DESC, song.title ASC) AS Rnk, song.title, album.title AS album_name, artist.name AS artist_name, id
            FROM song_saves
            LEFT JOIN song ON id = song.song_id
            LEFT JOIN artist ON song.artist_id = artist.artist_id
            LEFT JOIN album ON song.album_id = album.album_id
            LIMIT 100;
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