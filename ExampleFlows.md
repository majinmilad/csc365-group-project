# Example Flows– Provide in ExampleFlows.md
Examples for how endpoints will be called and satisfy use cases/ user stories (at least 3)

## Create Playlist
Milad wants to Create a Playlist and add music to it
- He starts by calling POST user/{user_id}/playlists/createplaylist
- then once the playlist is created he calls user/{user_id}/playlist/add_song
  
## Playlist Merging/ Recommendation Flow
Bob (user id: 1234) has saved a lot of playlists to his user account and wants to combine a select few of them to merge into a single playlist. 
  - He starts by calling GET /users/1234/playlists to retrieve all playlists he has saved to his account.
  - After reviewing the list, Bob selects playlists with IDs 5 and 6 to merge. He calls POST /playlists/merge, providing the list of playlist IDs. The system generates a draft playlist– “merged playlist #54” with ID: 54– by combining songs from the selected playlists, avoiding duplicates. 
  - Bob reviews the updated playlist and decides to change the title from "merged playlist #54" to "Best Playlist Ever." He calls PATCH /playlists/54/update, providing the new title.
  - Once satisfied, Bob saves the playlist to his account by calling POST /users/1234/playlists/save with the playlist ID 54. The playlist is now finalized and available in his account.

## Adding contributor to playlist
Edson(user id: 47) wants to add his friend as a collaborator for one of his playlists
  - He starts by calling GET /users/1234/playlists to retrieve all playlists he has saved to his account.
  - He then calls POST/users/{id}/playlists/{id} to retrieve a particular playlist he wants share
  - Finally he calls POST/playlists/{id}/collaborators to add his friend to his playlist
  - If his friend starts adding trash music or is messing with the vibe they can remove them with DELETE/playlists/{id}/collaborators/{collaborator_id}

## Controlling privacy settings
Jeremy's (user id: 100) ex-girlfriend keeps stalking his playlists how could Jeremy combat this
  - He calls PUT/playlists/{id}/privacy and is able to change the privacy settings on his account and playlists to friends-only. 
