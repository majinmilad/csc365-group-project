# CSC 365 Group Project: Technical Specification

## API Specification– Provide in APISpec.md
Endpoint documentation (at least 8 and mixture of read/ write endpoints)

# admin
POST/admin/song/{name}/{album}/{artist} -> add songs to database
  - Parameters: (song_name, album_name, artist_name)
  - Response:
    status_code = 204
    
# analytics
GET/analytics/playlists -> get most popular playlists
  - Parameters: none
  - Response: 
    list[ {“popularity”: integer, “title”: string, “id”: integer} ]

GET/analytics/songs -> get most popular songs
  - Parameters: none
  - Response: 
    list[ {“popularity”: integer, “name”: string, "album": string, "artist": string, "id”: integer} ]

# search
GET/search/playlists/{name} -> search playlist in database
- Parameters: (playlist_name)
- Response:
    list[ {“id”: integer, “name”: string, "followers": integer }] 

GET/search/songs/{name} -> search song in database
- Parameters: (song_name)
- Response
    list[ {"id": integer, "popularity": integer, "name": string, "album": string, "artist": string, "duration": integer} ]]

# users
POST/users/create -> create a user account
- Request: {"first_name": string, "last_name": string, "ssn": integer}
- Response:
    {"user_id": integer}, status_code=201

DELETE/users/delete -> delete a user account
- Request: {"user_id": integer}
- Response
    statuscode=200

GET/users/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_id} -> add a collaborator to a playlist
- Parameter: (user_id, playlist_id, collaborator_id)
- Response
    statuscode=200
  
DELETE/users/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_id} → remove a collaborator from a playlist
- Parameters: (user_id, playlist_id, collaborator_id)
- Response
    statuscode=200

PATCH/users/{user_id}/playlists/{playlist_id} -> update playlist name
- Parameters: (user_id, playlist_id, collaborator_id)
- Response
    statuscode=200
  
# playlists

GET/playlists/all -> retrieve all playlists
- Parameters: None
- Response:
    list[ {"playlist_id": integer, "playlist_name": string} ]

GET/playlists/{user_id}/all-playlists -> retrieve all created and followed user playlists
- Parameters: (user_id)
- Response:
    list[ {"playlist_id": integer, "playlist_name": string} ]

GET/playlists/{user_id}/playlists -> retrieve all created user playlists
- Parameters: (user_id)
- Response:
    list[ {"playlist_id": integer, "playlist_name": string} ]

POST/playlists/{user_id} -> create a playlist
- Parameters: (user_id, new_playlist_name)
- Response:
    {"new_playlist_id": integer}

POST/playlists/{user_id}/merge/{playlist_one}/{playlist_two} -> merge two playlists to create a new one
- Parameters: (user_id, playlist_one_id, playlist_two_id)
- Response:
    {"new_merged_playlist_id": integer}

DELETE/playlists/{user_id}/playlist/{playlist_id} -> delete a playlist
- Parameters: (user_id, playlist_id)
- Response:
    status_code=204

GET/playlists/{playlist_id}/songs -> get all songs from a playlist
- Parameters: (playlist_id)
- Response:
    [ {"song_id": integer, "track": string } ]

GET/playlists/songs/{song_id} -> get more info on a song
- Parameters: (song_id)
- Response:
    [ {"song_id": integer, "title": string, "album": string, "duration": stringer} ]

POST/playlists/{playlist_id}/songs/{song_id} -> add song to playlist
- Parameters: (song_id, playlist_id)
- Response:
    statuscode=204
  
DELETE/playlists/{playlist_id}/songs/{song_id} -> remove song from playlist
- Parameters: (user_id, playlist_id)
- Response:
    statuscode=204

POST/playlists/{user_id}/playlist/{playlist}/follow -> adds user as follower for playlist
- Parameter: (user_id, playlist_id)
- Response:
    statuscode=204

DELETE/playlists/{user_id}/playlist/{playlist}/unfollow -> removes user as follower from playlist
- Parameter: (user_id, playlist_id)
- Response
    statuscode=200

# Complex Endpoints
GET/admin/{name}/{album}/{artist} -> adds songs to database
- Parameters: Song_name
- Response
    [ {
  "id": string, "name": string, "type": string, "genres": [string], "popularity": int, "followers": int} ]

GET/{user_id}/merge/{playlist_one}{playlist_two} -> merge two playlists into a new playlist
- Paramters: (user_id, playlist_one_id, playlist_two_id)
- Response:
    {"new_merged_playlist_id": integer}

 
