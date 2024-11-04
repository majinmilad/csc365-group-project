# Example Workflow
Milad wants to Create a Playlist and add music to it
- He starts by calling POST user/{user_id}/playlists/createplaylist
- then once the playlist is created he calls user/{user_id}/playlist/add_song

# Testing Results
First line
1. curl -X 'POST' \
  'https://csc365-group-project-render.onrender.com/user/0/playlist/create_playlist?playlist_name=Edson%27s%20Playlists' \
  -H 'accept: application/json' \
  -d ''
2. 13 (which is the playlist id)

Second Line
1. curl -X 'POST' \
  'https://csc365-group-project-render.onrender.com/user/0/playlist/add_song?song_id=1&playlist_id=13' \
  -H 'accept: application/json' \
  -d ''
2. "Ok"
