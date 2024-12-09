## Product Ideas - Jonathan Martin

1 - Account Creation, login/signup
- Since this project relies on users having accounts attached to their playlists I feel some kind of login or at the very least a signup option is necessary so users don't use each other's user ids. 
- This could just require making Create and Delete account API endpoints and that'd be enough so users know what playlists are theirs 
- this could also require putting in passwords for any API endpoint requiring a user_id depending on the permissions you want to give people who aren't the users making playlists.

2 - adding collaborator permissions
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

## Code Review Comments - Jonathan
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

## Response - Megan
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

## Product Ideas - Connor
# 1.  Searching a Playlist
As a playlist increases in size, it becomes increasingly more painful to manually look through the playlist for a specific song. Thus, along with being able to list the contents of a playlist, being able to search a playlist would be an interesting feature. Similar to how the potion shop's `search_page` allows for searching for different attributes and ordering the results, a similar feature would be interesting.

# 2. Song Recommendations
Another interesting feature would be to recommend songs to users that are not in a selected playlist. Perhaps by looking at the amount of time an `artist` or `album` appears in a playlist relative to others, predictions could be made about what songs to recommend to the user.

## Response - Edson
these are both great ideas we did implement a search feature, but did not get around to doing recommendations

## Schema/API Design - Connor
1. This seems odd that `user_id` can be nullable. Unless there is a genuine use for this, consider disabling this.
https://github.com/majinmilad/csc365-group-project/blob/da13d40760ec998ffbf1c7cce6728618d58356ca/schema.sql#L4
2. Foreign key relations for `user_id` and `playlist_id` would be a useful addition. For example, this would prevent a playlist from getting created for a user that doesn't exist. Foreign key relations for `song_id` would be useful as well.
https://github.com/majinmilad/csc365-group-project/blob/da13d40760ec998ffbf1c7cce6728618d58356ca/schema.sql#L4-L5
3. Looking at the ER Diagram, there appears to be tables here that are missing from the Schema that could be useful to have. The `Tracks` and `PlaylistTracks` tables would be useful additions to the existing state of the project.
4. If the `Tracks` table is implemented, consider adding a function that allows the user to search this table for `track_titles`.
5. Again, looking at the ER Diagram, the `Playlist` table does not include a `user_id`, so there is no association between a playlist and the user it belongs to. Consider adding an `owner` role to `Collaborators` to solve this.
6. The `Playlist` table on the ER Diagram does not need a `number_of_tracks` column. This can be calculated when needed using the following:
```SQL
select
    count(track_id) as number_of_tracks
from
    PlaylistTracks
where
    playlist_id = :playlist_id
``` 
7. Consider using `playlist_title` as a parameter for functions instead of `playlist_id`. Then the user is not responsible for keeping track of the id of their playlist. This may require making the titles unique per user. Below is one such function that could benefit from this.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/APISpec.md?plain=1#L11-L14
8. The goal of this function is unclear. Currently, it is taking a `playlist_id` as a parameter and returning it along with a `title` and an `artist`. `artist` is not playlist specific, but rather track specific. Perhaps, this function should return the `playlist_title` along with a list of tracks in the playlist. See below for an example.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/APISpec.md?plain=1#L11-L14
```
Response:
{
    'playlist_title': A string that represents the title of the given playlist.
    'results': An array of objects, each representing a track. Each track has the following properties:
        - 'track_title': A string that represents the title of a specific track.
        - 'track_artist': A string that represents the artist of a specific track.
        - 'track_album': A string that represents the album a specific track is from.
        - 'duration': An integer representing the duration of a track in seconds.
}
```
7. Consider splitting this up into multiple functions, ie. `add`, `remove`, `update_title`, etc. As is, it appears a single function is responsible for multiple possibilities.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/APISpec.md?plain=1#L26-L29
9. The status of the request should not be included in the response body. Instead, an appropriate status code should be presented. See [FastAPI documentation](https://fastapi.tiangolo.com/tutorial/response-status-code/#about-http-status-codes) for implementation and the following [link](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) for a list of status codes.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/APISpec.md?plain=1#L29
10. The `collaborator_id` was used in the request body of adding a collaborator, but it is used in the URL for deleting a collaborator. It is best to stay consistent here. I would recommend keeping the `collaborator_id` in the request body or making it a parameter.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/APISpec.md?plain=1#L45-L48
11. Should this be a `PUT` instead of `POST`, since it is idempotent? See [link](https://www.theserverside.com/blog/Coffee-Talk-Java-News-Stories-and-Opinions/PUT-vs-POST-Whats-the-difference#:~:text=The%20key%20difference%20between%20PUT,identified%20by%20the%20URL%20provided.) for clarifaction.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/APISpec.md?plain=1#L40-L43
12. In the code, all endpoints begin with `/users/{user_id}`. Consider documenting this in the APISpec.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/main.py#L18
13. What is the idea behind `playlists/save` if `playlists/merge` automatically assigns the newly created merged playlist to the user?
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/APISpec.md?plain=1#L21-L24

## Response - Edson
1. that is no longer nullable
2. we now use foreign keys for users and playlists
3. we added a playlist songs and playlist table
4. we implemented a feature similar to that in search
5. the playlist tables includes the owner id
6. that was not implemented into the code
7. we chose not to do that to avoid issues in searching
8. this function was not implemented
7(2). this function was split into multiple functions as suggested
8(2). responses only return codes unless they are errors.
9. redudancies like these were addressed 
10. no, we add a new collaborator every time this is called
11. updated APIspec.md to align with our existing endpoints
12. playlist merge allows two playlists to be combined to make a new playlist; also playlist save was not implemented instead we added a follow feature


## Code Review Comments - Connor
This seems like a pretty cool project that has a lot of potential.

Code-wise, here are a few things that I think can be improved.

1. As for the project's structure, I recommend creating an API folder, similar to the potion shops, and a docs folder for the miscellaneous files. This can help keep the main directory less cluttered. Adding on to the API folder suggestion, separating your functions into individual files can make delegating work and expanding on the project easier.
2.  The Postgres URI shouldn't be here, and it exposes your database password. I see that your `.gitignore` includes a `.env` file, so consider adding the Postgres URI here.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/main.py#L8
3. If `database.py` is not being used, consider removing the file. Currently, the entire file is being commented out.
4. Currently, there is no code that interacts with the `user` table. As a result, code like this, which appears in each function, assumes a user exists and does not check otherwise.
https://github.com/majinmilad/csc365-group-project/blob/da13d40760ec998ffbf1c7cce6728618d58356ca/main.py#L24-L25
5. This function takes `user_id` as a parameter, but does not utilize it in any way. Perhaps it can be used to verify ownership of the playlist. Otherwise, it could be removed.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/main.py#L38-L46
6. Instead of relying on indices when appending to this list, consider using the column names instead. This can help your code be more readable for yourself and others. See below for an example.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/main.py#L50-L59
`playlist_list.append({'playlist_id': playlist.playlist_id, 'playlist_name': playlist.playlist_name})`
7. Perhaps instead of having the user provide a `song_id` or `playlist_id`, have them provide a `song_name` and `playlist_name`. This way, the user does not need to know the id of anything in order to add to a playlist. Two additional lookups would be required to find the `id` of each. This can be applied to all functions that use these parameters.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/main.py#L38
8. There is currently no function that displays the content of a playlist.
9. The APISpec and Example Flows mention a save function `POST /users/{user_id}/playlists/save` but this function does not exist.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/APISpec.md?plain=1#L21-L24
10. The same `user_id` can be added as a collaborator for the same playlist multiple times.
11. Any `playlist_id` can be used when adding a collaborator, regardless of existence. Consider verifying the existence of the playlist before adding a collaborator.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/main.py#L132-L142
12. Anyone can add or remove a collaborator from any playlist, regardless of ownership. Consider adding an additional parameter for a `user_id` and checking if the user who is making the request is the owner of the playlist or an existing collaborator.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/main.py#L145-L155
13. Things from local testing, such as this, can be removed. Tests could be placed in a separate file that is ignored in the `.gitignore`.
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/main.py#L158-L162
14. For functions that return information, consider formatting what is being returned so that the user can make sense of the information. For example, changing the following:
https://github.com/majinmilad/csc365-group-project/blob/a5b229074cade37d3a83fc3930810a29d6b0a9d6/main.py#L19-L34
```
return {"playlist_id": playlist_id}
```

## Response - Edson
1. api files were split
2. created an .env file
3. used database.py to run the connect to supabase
4. checking user existence has been implemented across most functions(were assuming that if there was a ui there wouldn't be a need for this check)
5. playlist ownership verification has also been added
6. updated cases like these to use column names instead of indices
7. we would implement this if we had a frontend for now we will continue using id's
8. view_playlist now shows songs in a playlist
9. the merge function exists and allows users to combine two playlists into a new one
10. added checks for edge cases like these in all functions
11. same as above
12. same as above
13. stuff from local testing has now been mostly removed
14. for now we will keep returning id's to avoid any complications with obtaining being able to access specific users, but we added a message that lists what the user is receiving

## Product Ideas - Nathan
1. From your API spec, it looks like you have a way to mark playlists as public or private. It would be cool if you had some way to browse public playlists. Perhaps you could do this by using the listening statistics, and adding an endpoint like `GET /playlists/popular` that would return the top 10 most listened to playlists.

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/APISpec.md?plain=1#L31-L34

2. Some sort of recommendation algorithm would be interesting. Something where you would track which songs each user listens to the most. Then, you could recommend songs to users with similar taste. For example, if User1 really enjoys listening to SongA and SongB, and User2 also really enjoys listening to SongA, but hasn't yet listening to SongB, you could recommend SongB to User2.

## Response - Edson

this is a great idea, we implemented a feature that allows users to view a general variety of playlists, but we might update that

## Scheme/API Design - Nathan
1. Not sure if this is a valid use case, but it seems odd to have user_id be nullable

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/schema.sql#L14

2. Looking at your ERD, you might want to consider making a separate table for artists and albums. This way, you could have a foreign key reference in tracks to albums, to show which album it's in. This would reduce redundancy (each album has an associated artist, so you'd only need to store album in the tracks table) and remove the possibility of an anomaly where an album can have multiple different artists across multiple rows.

3. In your ERD, it looks like you don't have a `user_id` attribute on playlist, but you do in your schema.sql. It looks like you're going to have a `collaborators` table, based on your ERD. What if instead of having a `user_id` on `playlist`, you instead tracked ownership with collaborators, by inserting a user with the `role` "owner"?

4. In your ERD, you have an attribute on the `playlist` table called `number_of_tracks`. This is duplication of data, and should probably be removed. You can compute the `number_of_tracks` instead, by doing something like this:

```sql
SELECT playlist.playlist_id, title, COUNT(track_id) AS number_of_tracks FROM playlist
JOIN playlist_tracks ON playlist.playlist_id = playlist_tracks.playlist_id
GROUP BY playlist.playlist_id, title
```

5. You should probably have one unique endpoint for every function (in this example, I would choose the `GET /playlist/{id}` one)

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/APISpec.md?plain=1#L11

6. Status of the request should not be included in the response body (if the request returns a 200, that implies it was a success), you should instead use [HTTP response code headers](https://developer.mozilla.org/en-US/docs/Web/HTTP/Status) for this

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/APISpec.md?plain=1#L18-L19

7. Is returning the `playlist_id` useful here? Since it was included in the request

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/APISpec.md?plain=1#L28-L29

8. Should this be a PUT request, since it's idempotent?

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/APISpec.md?plain=1#L40

9. Why is `collaborator_id` in the request body for adding, but a URL parameter for DELETE? It should be consistent

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/APISpec.md?plain=1#L40-L48

10. Why is this an array? Shouldn't it be a single dict instead?

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/APISpec.md?plain=1#L14

11. Looking in the API spec you don't seem to have an endpoint for creating playlists. Looks like you have one in your python code, but I would make the request `POST /user/{user_id}/playlist` instead.

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/main.py#L18

12. You have `POST /user/{user_id}/playlist/add_song` in your python code, but in your API spec it's listed as `PATCH/playlists/{id}/update`

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/main.py#L37

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/APISpec.md?plain=1#L26

## Response - Edson 
1. it is no longer nullable
2. we created separate tables for artists, albums was not used. used foreign keys to relate users, songs, and playlists 
3. We chose to not go forward with that because we felt it we be more efficient to keep the owners and collaborators separate.
4. We never used number of tracks
5. we have unique endpoints for all functions
6. updated all responses to only include a message if it was an error
7. that was fixed in the code
8. no, we are adding a single new collaborator every time this is called
9.  made all create and delete counterpart functions consistent
10. fixed that in the code 
11. adopted your suggested request
12. updated API spec

## Code Review Comments - Nathan

Hey guys! Very cool project, looks like it has a ton of potential.

Here's a few things I found that could be improved on:

1. Overall structural comment, you should consider splitting your code into multiple files, and using folders to keep things organized. I like the method the potion shop uses, where there's an `api` folder, and each file contains a particular section of the API.

2. Stuff like this should probably be moved into environment variables (and when you do, you should probably update your postgres password, because this will still be visible in the commit history):

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/main.py#L8

3. I'm not sure if this would work, but if SQLAlchemy is able to convert python `None` into postgres `null`, you could simplify this a bit

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/main.py#L23-L32

```py
# insert a new playlist into table
sql_to_execute = 'INSERT INTO playlist (user_id, playlist_name) VALUES (:user_id, :playlist_name) RETURNING playlist_id'
result = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': user_id, 'playlist_name': playlist_name})
```

4. You should probably handle the error case here and return a 400-level response, when an id is provided for a song or playlist that doesn't exist, see https://fastapi.tiangolo.com/tutorial/handling-errors/

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/main.py#L37-L46

5. Same as above, but for when `user_id` doesn't exist

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/main.py#L18-L34


6. Looks like `user_id` is required here, but it's not being used

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/main.py#L37-L38

7. Unused import that can be removed

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/main.py#L1

8. `playlist_name` should be typed as `str | None`, since it has the possibility of being `None`

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/main.py#L19

9. You should generally have all your imports at the top of the file, and not have any code between them

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/main.py#L1-L6

10. Stuff like this (local development setup and where to find the docs page) should ideally be put in the readme, as it's easier to find.

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/project_notes.txt#L6-L11

11. This file can be removed, as it's all commented out

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/database.py#L1-L10

12. Stuff left over from local testing that can be removed

https://github.com/majinmilad/csc365-group-project/blob/55775728bc17594488a91a34723e994585f2f860/main.py#L50-L51

## Response 

1. split api into multiple files
2. created .env file
3. simplified the express by using if(playlist_name):
4. all edge cases have been covered to return some error code
5. same as above
6. got rid of unnecessary data parameters
7. got rid of unused modules
8. made it so that a playlist must be called something
9. all imports were moved to the top
10. moved all documentation to readme.md
11. most unnecessary code comments were removed
12. removed must commented testing comments
