# User Stories and Exceptions (DRAFT)

## User Stories
- As a user I would want my playlist to update in real time so they are readily available
- As a user I would want a daily song recommendation to expand my music taste
- As a user I would want my daily listening statistic to see what I listen to the most
- As a user I would like to Share playlists between platform/Convert playlists so that friends on different platforms can listen to the music
- As a user I would like to view all playlists on a profile maybe all together or on either app so that they are easily accessible
- As a user I would like to share what you're currently listening to so that I can see friends music
- As a user I would like an add friends feature to see other's playlists
- As a user I would like to Remove friends in case they have bad taste
- As a user potentially having Friend Recommendations would be nice if I want to see what mutuals are listening to
- As a user I would also like Privacy Control Settings so that people aren't stalking my music
- As a user I would like to a ranking of playlists by how often I listen to them
- As a user I would like to see the most popular playlist too based on how liked it is collectively

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
