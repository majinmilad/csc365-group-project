# Example Workflow
## Playlist Merging/ Recommendation Flow
Bob (user id: 1234) has saved a lot of playlists to his user account and wants to combine a select few of them to merge into a single playlist. 
  - He starts by calling GET /users/1234/playlists to retrieve all playlists he has saved to his account.
  - After reviewing the list, Bob selects playlists with IDs 5 and 6 to merge. He calls POST /playlists/merge, providing the list of playlist IDs. The system generates a draft playlist– “merged playlist #54” with ID: 54– by combining songs from the selected playlists, avoiding duplicates. 
  - Bob reviews the updated playlist and decides to change the title from "merged playlist #54" to "Best Playlist Ever." He calls PATCH /playlists/54/update, providing the new title.
## Adding contributor to playlist
Edson(user id: 47) wants to add his friend as a collaborator for one of his playlists
  - He starts by calling GET /users/1234/playlists to retrieve all playlists he has saved to his account.
  - He then calls POST/users/{id}/playlists/{id} to retrieve a particular playlist he wants share
  - Finally he calls POST/playlists/{id}/collaborators to add his friend to his playlist
  - If his friend starts adding trash music or is messing with the vibe they can remove them with DELETE/playlists/{id}/collaborators/{collaborator_id}

# Testing Results
##Playlist Merging/ Recommendation Flow
First Line
1. curl -X 'GET' \
  'http://127.0.0.1:8000/users/69/playlists' \
  -H 'accept: application/json'
2. [
  {
    "playlist_id": 17,
    "playlist_name": "oldies"
  },
  {
    "playlist_id": 18,
    "playlist_name": "new_oldies"
  },
  {
    "playlist_id": 19,
    "playlist_name": "updated_oldies"
  },
  {
    "playlist_id": 20,
    "playlist_name": "outdated_oldies"
  }
]

Second Line
1. curl -X 'POST' \
  'http://127.0.0.1:8000/users/69/playlists/merge?new_playlist_name=updated_oldies' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '[
  17, 18
]'
2. {
  "new_playlist_id": 20,
  "message": "Playlists merged"
}

Third Line
1. curl -X 'PATCH' \
  'http://127.0.0.1:8000/users/69/playlists/20/update?new_name=outdated_oldies' \
  -H 'accept: application/json'
2. {
  "message": "Playlist updated"
}

##Adding Contributor to Playlist
