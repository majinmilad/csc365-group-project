EXPLAIN ANALYZE
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
