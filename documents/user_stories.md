# User Stories and Exceptions

## User Stories
- As a modern software consumer who expects changes to be reflected in real time, I would want my playlist to update in real time so they are readily available
- As a music listener looking to discover new music, I would want a daily song recommendation to expand my music taste
- As a reflective music listener, I would want my daily listening statistic to see what I listen to the most
- As a social user using a specific music streaming platform, I would like to share playlists between platforms/convert playlists so that friends on different platforms can listen to the music
- As a user looking to explore others' playlists, I would like to view all playlists on a profile in totality so that they are easily explorable
- As a social user, I would like for others to be able to share what they're currently listening to so that I can see my friends listening habits in real time
- As a social user, I would like the ability for an add-friends-feature so I can track friends' playlists and listening habits
- As a social user with my own musical opinions, I would like the ability to remove friends in case I disagree with their taste or no longer associate with them
- As a social user looking to expand my social network, having Friend Recommendations would be a nice feature if I want to see what mutuals are listening to
- As an individual user, I would also like Privacy Control Settings so that people aren't stalking my music and I can control what others can view about my account activity
- As an organized application user, I would like a ranking of playlists based on how often I listen to them
- As a explorative user, I would like to see the most popular playlists based on how liked, listened to or followed they are across all users collectively

## Exceptions

Exception: Mismatch in playlists
  If playlists don't match up on platforms an error flag will be raised

Exception: A playlist is deleted
  If a user wants to remove a playlist they will be asked what apps to remove it on

Exception: User has no data on account
  User will be prompted to enter data

Exception: Same artists between platforms do not match
  Error will be raised; Some margin of error between artists names will be allowed

Exception: Songs don't exist on both platforms
  Error will be raised and user will be asked if they still want to add the song

Exception: Artists removes a song from discography
  Song will be grayed out and user will be prompted to remove or keep the song

Exception: Artist no longer exists
  Music will be grayed out and user will be prompted to remove or keep the song

Exception: What if songs are different between platforms
  A margin of error will be allowed between songs

Exception: User wants to create playlist on platform
  This is up in the air at the moment

Exception: Playlist is updated on either platform
  Users with playlist added will be prompted to accept the updates or not (branch the playlist?)

Exception: Playlist is made private
  The user with the playlist updated will no longer receive updates if the playlist is updated

Exception: User tries to add the same playlist twice
  The user will be asked if he want to overwrite current playlist
