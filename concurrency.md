# Concurrency Control Scenarios

## Case 1: Dirty Read In Playlist Synchronization 
**Scenario**
- Issue: A playlist is being synchronized with an external platform (ex. Spotify) while a user is simultaneously adding tracks to the playlist. If the synchronization transaction reads uncommitted track additions, the synced playlist might include tracks that don't exist if the addition transaction rolls back.
- Example: Syncing a playlist to Spotify while uncommitted tracks are being added 
- Solution: Set the isolation level to READ COMMITTED to ensure only committed tracks are included during synchronization
- Sequence Diagram: 
```
T1: Begin Transaction (Adding Tracks)
T1: Insert Track into PlaylistTracks (Uncommitted)
T2: Begin Transaction (Synchronizing Playlist)
T2: Read PlaylistTracks Table (Includes T1's Uncommitted Tracks)
T1: Rollback Transaction
T2: Sync Playlist with Non-existent Track 
```
- Isolation Level: READ COMMITTED
  - Ensures synchronization reads only committed track data, preventing syncing of incomplete or rolled back changes.

## Case 2: Non-Repeatable Read in Playlist Metadata Updates
**Scenario**
- Issue: Two users attempt to update the same playlist’s metadata (e.g., title or description). One user updates the title, while the other updates the privacy setting. Without proper isolation, the final state of the playlist may inconsistently reflect changes.
- Example: User A changes the title while User B changes the privacy setting.
- Solution: Use REPEATABLE READ isolation level to ensure that updates to the playlist are consistent within a single transaction.
- Sequence Diagram:
```
T1: Begin Transaction (User A)
T1: Read Playlist Metadata (Title: "Chill Vibes", Privacy: "Private")
T2: Begin Transaction (User B)
T2: Update Playlist Privacy to "Public"
T2: Commit Transaction
T1: Update Playlist Title to "Relaxing Tunes"
T1: Commit Transaction
Result: Playlist Metadata (Title: "Relaxing Tunes", Privacy: "Private") is inconsistent.
```
- Isolation Level: REPEATABLE READ
  - Guarntees that metadata reads are consistent within the transaction, preventing lost updates/ conflicting changes.

## Case 3: Phantom Read in First-Time Collaboration Check
**Scenario**
- Issue: A user invites a collaborator to a playlist while another user simultaneously adds a different collaborator. If the first transaction checks for existing collaborators, it might incorrectly assume this is the first collaboration and apply unnecessary notifications or permissions.
- Example: User A and User B invite collaborators at the same time.
- Solution: Use SERIALIZABLE isolation level to ensure no new rows (collaborators) are added during the transaction.
- Sequence Diagram:
```
T1: Begin Transaction (User A)
T1: Query Collaborators Table (No Existing Collaborators)
T2: Begin Transaction (User B)
T2: Insert Collaborator into Collaborators Table
T2: Commit Transaction
T1: Re-query Collaborators Table
T1: Apply "First Collaboration" Logic (Incorrectly Assumes No Collaborators)
T1: Commit Transaction
```
- Isolation Level: SERIALIZABLE
  - Ensures no new collaborators can be added to the table while the transaction checks for existing collaborators. 
