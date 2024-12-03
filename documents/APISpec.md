# CSC 365 Group Project: Technical Specification

## API Specification– Provide in APISpec.md
Endpoint documentation (at least 8 and mixture of read/ write endpoints)

GET/users/{id}/playlists → retrieve all playlists associated with a user 
  - Parameters: id (unique identifier of user)
  - Response: 
    [ {“playlist_id”: integer, “title”: “string”, “number_of_tracks”: integer} ]

GET/users/{id}/playlists/{id} → retrieve a single unique playlist(could also be GET/playlist{id}) if we have unique id’s for every playlist)
  - Parameters:user id( unique identifier of user) playlistid(unique identifier of playlist)
  - Response:
    [{“playlist_id”: integer, “title”: “string”, “artist”: “string”}]

POST/playlists/merge → merge a list of playlists into a single playlist
  - Request: {“playlist_ids”: []}
  - Response: 
  - {“merged_playlist_id”: integer, “status”: “success or failure”}

POST/users/{id}/playlists/save → save the merged playlist to their user account
  - Parameters: id (unique identifier of user)
  - Request: {“playlist_id”: integer}
  - Response: {“saved_playlist_id”: integer, “status”: “success or failure”}

PATCH/playlists/{id}/update → add/ remove songs, modify title, or change playlist description
  - Parameters: id (id of playlist; must be a saved playlist to the user’s account)
  - Request: {“title”: “string”, “description”: “string”, “tracks”: []}
  - Response: {“playlist_id”: integer, “status”: “success or failure”}

PUT/playlists/{id}/privacy → update privacy settings of a playlist (public, private, friends-only)
  - Parameters: id (id of playlist; must be a saved playlist to the user’s account)
  - Request: {“privacy”: “public, private, or friends-only”}
  - Response: {“playlist_id”: integer, “privacy”: “string”, “status”: “success or failure”}

GET/playlists/{id}/statistics → retrieve listening statistics for a playlist (play count, top songs, top artists, etc)
  - Parameters: id (id of playlist; must be a saved playlist to the user’s account)
  - Response: {“play_count”: integer, “top_tracks”: [], “top_artists”: []}

POST/playlists/{id}/collaborators → add a collaborator to a playlist for collaborative editing 
  - Parameters: id (id of playlist; must be a saved playlist to the user’s account)
  - Request: {“collaborator_id”: integer}
  - Response: {“playlist_id”: integer, “collaborators”: [], “status”: “success or failure”}

DELETE/playlists/{id}/collaborators/{collaborator_id} → remove a collaborator from a playlist that you own 
  - Parameters: id (id of playlist; must be a saved playlist to the user’s account)
  - Id of collaborator you want to remove
  - Response: {“playlist_id”: integer, “collaborators”: [], “status”: “success or failure”}

# Complex Endpoints
GET/search/{song_name} ->
- Parameters: Song_name
- Response
    [ {
  "id": string, "name": string, "type": string, "genres": [string], "popularity": int, "followers": int} ]

GET/search/{artist_name} ->
- Paramters: artist_name
-Response: [{ "id": string, "name": string, "type": string, "genres": [string], "popularity": int, "followers": int }]
 
