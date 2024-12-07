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