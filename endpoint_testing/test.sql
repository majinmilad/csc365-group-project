SELECT user_account.user_id, first_name, last_name, COUNT(playlist_id) AS num_playlists FROM user_account
JOIN playlist ON playlist.user_id = user_account.user_id
GROUP BY user_account.user_id, first_name, last_name
ORDER BY COUNT(playlist_id) DESC, user_account.user_id DESC
LIMIT 100;

SELECT user_account.user_id, first_name, last_name, COUNT(playlist_id) AS num_follows FROM user_account
JOIN playlist_follower ON playlist_follower.user_id = user_account.user_id
GROUP BY user_account.user_id, first_name, last_name
ORDER BY COUNT(playlist_id) DESC, user_account.user_id DESC
LIMIT 100;

WITH top_followers AS (
    SELECT user_account.user_id, first_name, last_name, COUNT(playlist_id) AS num_follows FROM user_account
    JOIN playlist_follower ON playlist_follower.user_id = user_account.user_id
    GROUP BY user_account.user_id, first_name, last_name
    ORDER BY COUNT(playlist_id) DESC, user_account.user_id DESC
    LIMIT 100
),
top_posters AS (
    SELECT user_account.user_id, first_name, last_name, COUNT(playlist_id) AS num_playlists FROM user_account
    JOIN playlist ON playlist.user_id = user_account.user_id
    GROUP BY user_account.user_id, first_name, last_name
    ORDER BY COUNT(playlist_id) DESC, user_account.user_id DESC
    LIMIT 100
)
SELECT * FROM top_posters
JOIN top_followers ON top_posters.user_id = top_followers.user_id
ORDER BY num_playlists DESC, num_follows DESC

WITH Ranked_songs AS
            (
                SELECT song.song_id as id, song.title, album.title as album_name, artist.name as artist_name, playlist_song.playlist_id, COUNT(playlist_song.playlist_id) OVER (PARTITION BY song.song_id) AS saves
                FROM song
                LEFT JOIN playlist_song ON playlist_song.song_id = song.song_id
                JOIN album ON album.album_id = song.album_id
                JOIN artist ON artist.artist_id = song.artist_id
            ),
            Distinct_songs AS
            (
                SELECT DISTINCT Saves, Ranked_songs.title, album_name, artist_name, Ranked_Songs.id
                FROM Ranked_Songs
                LIMIT 100
            )
            SELECT RANK() OVER (ORDER BY saves DESC, title ASC) AS Rnk, title, album_name, artist_name, id
            FROM Distinct_songs

SELECT song.song_id as id, song.title, album.title as album_name, artist.name as artist_name, playlist_song.playlist_id, COUNT(playlist_song.playlist_id) OVER (PARTITION BY song.song_id) AS saves
                FROM song
                LEFT JOIN playlist_song ON playlist_song.song_id = song.song_id
                JOIN album ON album.album_id = song.album_id
                JOIN artist ON artist.artist_id = song.artist_id
                LIMIT 100

WITH Ranked_songs AS
    (
        SELECT song.song_id as id, song.title, album.title as album_name, artist.name as artist_name, playlist_song.playlist_id, COUNT(playlist_song.playlist_id) OVER (PARTITION BY song.song_id) AS saves
        FROM song
        LEFT JOIN playlist_song ON playlist_song.song_id = song.song_id
        JOIN album ON album.album_id = song.album_id
        JOIN artist ON artist.artist_id = song.artist_id
        LIMIT 100
    )
SELECT DISTINCT Saves, Ranked_songs.title, album_name, artist_name, Ranked_Songs.id
FROM Ranked_Songs

SELECT playlist.playlist_id as id, playlist_name, COUNT(playlist_follower.user_id) as followers
            FROM playlist
            JOIN playlist_follower ON playlist_follower.playlist_id = playlist.playlist_id
            WHERE playlist_name ILIKE :playlist_name
            GROUP BY id, playlist_name
            ORDER BY followers DESC

SELECT artist.name AS artist_name, COALESCE(COUNT(playlist_song.playlist_id) + COUNT(song.song_id), 0) AS popularity
FROM song
JOIN album ON album.album_id = song.album_id
JOIN artist ON artist.artist_id = song.artist_id
LEFT JOIN playlist_song ON playlist_song.song_id = song.song_id
WHERE artist.name ILIKE :artist_name
GROUP BY artist.name
ORDER BY popularity

-- @router.get("/artists/{name}")
-- def search_for_songs(artist_name: str = ''):
--     with db.engine.begin() as connection:
--         sql_dict = {
--             'artist_name': artist_name
--         }
--         sql_query = sqlalchemy.text("""
--             SELECT SUM(COALESCE(COUNT(playlist_song.playlist_id), 0), COALESCE(COUNT(song.song_id as id), 0)) AS popularity, artist.name as artist_name
--             FROM song
--             JOIN album ON album.album_id = song.album_id
--             JOIN artist ON artist.artist_id = song.artist_id
--             LEFT JOIN playlist_song ON playlist_song.song_id = song.song_id
--             WHERE artist.name ILIKE :artist_name
--             GROUP BY artist.name
--             ORDER BY popularity
--             """)
--         songs = connection.execute(sql_query, sql_dict).fetchall()
--         results = []
--         for song in songs:
--             results.append({
--                 'id': song.id,
--                 'popularity': song.popularity,
--                 'name': song.song_title,
--                 'album': song.album_title,
--                 'artist': song.artist_name,
--                 'duration': song.duration
--             })
--     return results

SELECT playlist_id, COUNT(song_id) FROM playlist_song
GROUP BY playlist_id
ORDER BY count(song_id) DESC
LIMIT 100

SELECT playlist_follower.playlist_id, playlist.user_id, COUNT(playlist_follower.user_id) AS followers, COALESCE(COUNT(playlist_song.song_id), 0) as songs FROM playlist_follower
JOIN playlist on playlist.playlist_id = playlist_follower.playlist_id
JOIN playlist_song on playlist.playlist_id = playlist_song.playlist_id
GROUP BY playlist_follower.playlist_id, playlist.user_id
ORDER BY followers DESC, songs
LIMIT 100

SELECT DISTINCT playlist.playlist_id, playlist.user_id, 
COUNT(playlist_follower.user_id) OVER (PARTITION BY playlist.playlist_id) AS followers,
COUNT(playlist_song.song_id) OVER (PARTITION BY playlist.playlist_id) as songs FROM playlist
JOIN playlist_follower on playlist.playlist_id = playlist_follower.playlist_id
JOIN playlist_song on playlist.playlist_id = playlist_song.playlist_id
WHERE playlist.playlist_id = 49148

WITH playlist_stats AS(
    SELECT playlist.playlist_id, playlist.user_id, 
    COUNT(playlist_follower.user_id) OVER (PARTITION BY playlist.playlist_id) AS followers,
    COUNT(playlist_song.song_id) OVER (PARTITION BY playlist.playlist_id) as songs FROM playlist
    JOIN playlist_follower on playlist.playlist_id = playlist_follower.playlist_id
    JOIN playlist_song on playlist.playlist_id = playlist_song.playlist_id
)
SELECT DISTINCT * FROM playlist_stats
WHERE followers = songs