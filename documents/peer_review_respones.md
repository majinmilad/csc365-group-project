## Product Ideas - Jonathan Martin

## 1 - Account Creation, login/signup
- Since this project relies on users having accounts attached to their playlists I feel some kind of login or at the very least a signup option is necessary so users don't use each other's user ids. 
- This could just require making Create and Delete account API endpoints and that'd be enough so users know what playlists are theirs 
- this could also require putting in passwords for any API endpoint requiring a user_id depending on the permissions you want to give people who aren't the users making playlists.

## 2 - adding collaborator permissions
- Along the same line as the previous idea is being able to add permissions when adding a collaborator. 
- This can either be an other parameter when calling 
-       "PATCH /users/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_user_id}"
- or an entirely different and specific endpoint such as 
-       "PATCH /users/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_user_id}/permissions/{permission_id}"

## Response - Megan
1. While the idea of account creation and authentication (e.g., login/signup) adds robustness and security, it is currently out of scope for our project. The existing user_id field in our database is designed solely to track ownership, collaboration, and followers for playlists. It does not correspond to an actual user authentication system, as this project focuses on playlist management rather than a full-fledged user account system.
2. Our platform is intentionally designed as a public playlist platform. Since all playlists are public, there's no need to differentiate between collaborators' permissions. The sole purpose of collaboration is to allow editing or managing playlists jointly. If a user wants to interact with a playlist without editing permissions:
   - They can follow the playlist, allowing them to save it for easy access.
   - They can merge it with their own playlists, creating a private copy with the desired songs.
Adding granular collaborator permissions would introduce unnecessary complexity for the current scope and philosophy of the platform, which is to prioritize openness and simplicity in playlist sharing.

## Schema/API - Design by Jonathan
1.  Should add a POST API for adding a user alongside the one you have for adding and deleting a collaborator since collaborators and many other parts of the schema depend on a user and there is no way for a user to be made.
2. Also add a DELETE user with password implementations as detailed by your ER-diagram, since this would be useful for people with multiple accounts. Part of implementing this may also include deleting playlists that user owned if you believe that would be necessary.
3. add a parameter to the "PATCH/playlists/{id}/update" that could indicate whether or not the user wants to alter any one of the 3 attributes or make it clear how not to alter things like tracklist or playlist title. For example if no parameter is given than nothing is changed and if an empty parameter is given for the tracklist, than it would delete/reset it.
4.  combining both "PATCH/playlists/{id}/update" and "PUT/playlists/{id}/privacy" as they both update different aspects of a playlist and require the us to choose what they want to and don't want to update in one instance.
5. combining both "POST/playlists/merge" and "POST/users/{id}/playlists/save" into one as they serve the same purpose and with the capability to DELETE a playlist the user can decide whether they want to keep the playlist.
6. add privacy parameter to "POST/users/{id}/playlists/save" since there is no way to set it on playlist creation, only after it is created using "PUT/playlists/{id}/privacy"
7. Unclear as to how "play_count" would be tracked in "GET/playlists/{id}/statistics", since it isn't tracked how many times a song is played in the schema.
8.  Adding password field to user, which would need implementation with login/signup API endpoints and for user/account deletion. 
9.  Add foreign key constraint to "user_id" in "playlist" table since it acts as a foreign key to the users table and allows the database to check for any issues occurring due to that. Or you can remove "user_id" from the "playlist" table since a join on the "playlist_song" table makes that connection
10. Both "user_id" and "playlist_id" in the "playlist_song" table should have foreign key constraints to their respective tables as that connection is the purpose of the table.
11. add "privacy" attribute to collaborator table, since that is part of the API specifications and purpose of adding collaborators, unless every collaborator will have the same permissions to a playlist
12. add collaborator permissions field, similar to privacy for a list to separate different permissions between different collaborators such as view only, view and add permissions and lastly view, delete and add permissions.

## Response - Megan
1. Yes we now have an endpoint that creates a user.
2. We have an endpoint that removes a user and every playlist they personally own. We chose not to implement this endpoint with a password requirement since creating a user only requires them to submit basic info-- first and last name and ssn. We also have an endpoint that allows a user to delete a playlist they own. 
3-4. We have replaced this endpoint with the option to just rename the playlist. To edit the playlist content, the user would have to call either our endpoint that adds a song to a playlist or our endpoint that deletes a song from a playlist. Since our product targets public playlist sharing, there are no privacy settings to be implemented. 
5. I see where you are going with this but we've decided to implement an endpoint that allows a user to simply follow a playlist instead of saving a copy of it. Given this modification, merge playlist stays separate. 
6. Since our product targets public playlist sharing, there are no privacy settings to be implemented. 
7. Yes, we decided that keeping record of this information is out of scope. 
8. We decided to not implement a login option for users. Users are created using their first name, last name, and ssn. 
9. Suggestion implemented.
10. Suggestion implemented. 
11. Since our product targets public playlist sharing, there are no privacy settings to be implemented. Collaborators are added to a playlist to collaboratively edit (add/ remove songs) a playlist. 
12. Our product targets public playlist sharing which means all users have the right to view every other playlist that exists in the db. Collaborators don't need a permissions field since they would only be added to collaborate on a playlist for editing purposes. A collaborator has the right to add/ remove songs and remove themselves as a collaborator from the playlist.

## Code Comments - Jonathan
1.  keep "main" branch of repository up to date as it was confusing seeing the "v2-draft" branch had the most up to date "main.py" to review the code and difficult to clone for testing.
2.  Maybe a guide was needed to for testing locally since I couldn't figure out how to do it from any version of the program, but it does run correctly on the render website so I was able to test it that way
3. on "create_playlist" function you should probably not create a playlist at all if a name wasn't provided by still testing for it before executing your "INSERT INTO" sql statement so that you only have to do one sql statement. This would still allow for the playlist_id to be set as it will be generated automatically.
4.  comments are misleading on "add_song_to_playlist" function saying "insert a new playlist into table" when it is inserting a song I presume.
5.  add tests for valid inputs on "add_song_to_playlist" function. Since it never checks if song_id or playlist_id point to valid entries on their respective tables. Can also be done by the database itself through the use of foreign key constraints.
6. on "get_user_playlist" function should be using "playlist.playlist_id" and "playlist.playlist_name" rather than indexing from the query for readability.
7. on "get_user_playlist" function should add a case when no playlists are returned with a message to inform the user
8. last statement of "merge_playlists" function is confusing due to the "if insert_data" as I presume "insert_data" to be a list of dictionaries and don't understand how this affects the if statement. However I'm from the comment i'm guessing this adds every new playlist and song id pair to the playlist_songs table. Overall just confusing python syntax for this function.
9. parameters in "update_playlist" allow for new_name to be NULL, but it isn't checked until after the update query is completed rather. Instead it should be done before, while still keeping the check after to see if the database was updated
10. database.py is completely commented out for an unknown reason, rendering the file useless and making me wonder when it is or was used in the project. Again, some documentation on these files would fix this.
11. Unclear as to what the statement that runs when main is run does as it is commented out, furthermore making it unclear how main.py is ran.
12. Similarly to my group project, in most instances a song_id or playlist_id is given in the API request when the users probably can't indentify them by ids. To fix this would be done by searching by the names of songs or playlist, but this might cause other issues and the UI of a website might account for the issue as the user may never interact with the API calls directly.

## Response 
1. Yes, we were a bit behind on merging our branches into main. Main is now fully updated. 
2. Our endpoints can be ran locally and tested on <server>/docs.
3. Good suggestion. Our "create_playlist" endpoint now requires the user to provide a playlist name. 
4. Comments now fully reflect what is being operated. 
5. Our "add_song_to_playlist" endpoint now validates the user_id, the song_id, the playlist_id, and checks to see if the user_id has playlist modification rights on the playlist being edited. 
6-7. Our "get_user_playlist" endpoint now retrieves all playlists a user owns, returning the playlist_id(s) and playlist_name(s). If there are no playlists to be returned it now returns a 404 response, indicating that no playlists were found. 
8. Get that this might be confusing, but the if statement is essential for verifying that there are songs to insert into the merged playlist. 
9. We have changed the endpoint to be "change_playlist_name" and it now requires for a new_name to be provided. We also validate that the user_id has permission to edit the playlist name before editing the name. 
10. database.py is now fully implemented. To run the program locally, run python main.py. 
11. We now have an endpoint returning all playlists owned by a user, an endpoint returning all playlist owned/ followed by a user, an endpoint returning the playlists in the db (owned by any user), an endpoint returning the song_ids in a playlist, and an endpoint that returns song information for a given song_id. These endpoints should help users identify unknown ids.
