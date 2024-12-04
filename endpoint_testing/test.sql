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