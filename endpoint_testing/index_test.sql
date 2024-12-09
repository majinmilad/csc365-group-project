-- Popular Songs
CREATE MATERIALIZED VIEW IF NOT EXISTS song_saves AS
    SELECT song_id as id, COUNT(playlist_song.playlist_id) AS saves
    FROM playlist_song
    GROUP BY song_id

CREATE INDEX IF NOT EXISTS idx_song_saves ON song_saves(saves);

EXPLAIN ANALYZE
SELECT RANK() OVER (ORDER BY saves DESC, song.title ASC) AS Rnk, song.title, album.title, artist.name, id
FROM song_saves
LEFT JOIN song ON id = song.song_id
LEFT JOIN artist ON song.artist_id = artist.artist_id
LEFT JOIN album ON song.album_id = album.album_id
LIMIT 100

-- Song Search
CREATE INDEX idx_playlist_track ON playlist_song(song_id);

EXPLAIN ANALYZE
SELECT COALESCE(COUNT(playlist_song.playlist_id), 0) as popularity, song.song_id as id, song.title as song_title, album.title as album_title, artist.name as artist_name, duration
            FROM song
            JOIN album ON album.album_id = song.album_id
            JOIN artist ON artist.artist_id = song.artist_id
            LEFT JOIN playlist_song ON playlist_song.song_id = song.song_id
            WHERE song.title ILIKE :song_name
            GROUP BY song.song_id, song.title, album.title, artist.name, duration
            ORDER BY popularity

