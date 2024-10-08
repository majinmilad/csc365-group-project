# csc365-group-project
Repository for the group project in CSC 365 at Cal Poly  

Members: Jackson McLaughlin, Edson Munoz, Megan Fung and Milad Chabok
- jdmclaug@calpoly.edu
- emunoz23@calpoly.edu
- mfung06@calpoly.edu
- mchabok@calpoly.edu

## Project Proposal (DRAFT)
The Playlist Exchanger is a platform where users can upload and share playlists between Spotify and Apple Music. Users can easily pull and update playlists, ensuring they always have the latest tracks. The system enables collaborative playlist creation by genre, allowing users to contribute to and curate genre-specific collections. Additionally, users can cross-join playlists based on attributes like genre, tempo, or mood, automatically generating mixed playlists. The use of joins in the database will facilitate complex operations, like merging playlists on shared attributes, providing a seamless experience for users to discover new music through collaborative and dynamic exchanges.

##User Stories and Exceptions (DRAFT)
User Stories
- As a user I would want my playlist to update in real time, database should match
- As a user I would want a daily song recommendation
- As a user I would want my daily listening statistic
- Share playlists between platform/Convert playlists
- View all playlists on a profile maybe all together or on either app
- Show what your currently listening to
- Add friends feature
- Remove friends
- Friend Recommendations???
- Privacy Control Settings
- Rank playlists based off how often it is listened to by the user
- Rank playlist based on how liked it is collectively

Exceptions
- How to handle if Spotify and Apple Music playlists don’t line up
- How to handle if a playlist is deleted
- What if user has no data on account
- How to determine if artists are the same between platforms
- How to tell if songs don’t exist on the other platform
- What to do if songs don’t exist on the other platform
- How to handle if an artists removes a song
- How to handle if an artists no longer exists
- What if the songs are different between platforms
- What to do if a playlist is created on the platform
- What if playlist is updated on either Apple Music or Spotify especially if it is a song the other does not have
- What if a playlist is updated on the platform


## Style Guide
### Git
#### Quick Summary
- Make commit messages clear, concise and in the present tense
- Use commit descriptions if necessary to provide futher detail on the commit's changes or the state of the code
- Branches should be heavily utilized to divide / delegate work and seperate stable code versions from work-in-progress versions
#### Commits
> [!NOTE]
> Make commit messages clear but concise and ***in the present tense***.  
*Examples:* "Add database.py file" "Implement writing user account info to database" "Improve readability of example_function()" "Fix user login bug"  
##### When to commit
Commit whenever you deem best, but it's common practice to make commits neither too large nor too small in scope. Usually, whenever you do some work you might consider to be a "single job" it's a good time to make a commit. If the job can't be described by a single concise commit message then it probably should have been broken into multiple commits. However, it's of course left to the discretion of the developer.  
##### Commit descriptions
Each commit has an optional description too. Use this (if desired) to expand on the commit message or write whatever you'd like regarding the commit work. If you do end up making a commit too large in scope to be adequetly described by a single commit message, make the best message you can and then use its description to explain in further detail the changes made by the commit. Descriptions can be in any tense you want (past or present) but I recommend the past tense.  
#### Branches
We have two ways we can delegate work. We can make a branch for each member and communicate what each person will be working on. Alternatively we can make branches (which are more temporary in nature) for individual jobs/features and assign people to work on these specific branches. We can discuss how we'd like to do it together.  
> [!NOTE]
> Branches should be styled with all lowercase and '-' instead of spaces e.g. "*edson-branch*" or "*stable-working*"

> [!IMPORTANT]
> The main branch should never be worked on directly. Either use an appropiate existing branch (and pull from main if desired) or create a new branch based on main for the developmental task at hand. These development branches will be merged back into main or stable-working when appropiate.
