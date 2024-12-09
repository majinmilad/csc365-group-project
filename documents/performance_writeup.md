# **Performance Writeup**

---


## **Generating Fake Data**
All scripts, and files for data generation are located in  [/endpoint_testing](https://github.com/majinmilad/csc365-group-project/tree/main/endpoint_testing).

**Rationale:** 
* Total songs:  23630, pulled from an online database of Billboard top 100 songs
* Total users:  10000, a reasonable expectation for a small but active community
* Total playlists:  128372, Divided into 3 groups based on reasearch into spotify's users. 

    About 60% of users aren't creators and only follow playlists(Similar percentage to spotify's free users). 

    Of users who make playlists, there's a normal distribution located at about 25 playlists on average(Spotify's average is about 12.8 playlists per user but this also accounts for users with 0 playlists). 

    Then an exponential curve is added on to represent "super users" who have 40 or more playlists spanning into the 100s(Spotify has users with 300 or more playlists).


* Total followers:  119299, Determined by 3 binomial distributions.  
    Majority of playlists end up with 0 to 5 followers, most with 0, this is calculated with a binomial distribution where p = a ratio between users and total playlists.

    Two Binomials were added to account for the highest performing playlists, the top 100 playlists were given a p = 0.1 or about a 10% chance to be followed. The top 10 most popular were given a p = 0.6 a little above a 50% chance to be followed. 
    
* Total collaborators:  12829, Collaborators were generated with a negative binomial distribution so that most playlists had 0. The number represents the count of users collaborating on each playlist, some users collaborate on multiple playlists so the count is slightly higher than total users.

* Total playlist contents:  3850422, Generated with a Poisson Distribution where lambda is 30, aproximmating 30 songs per playlist.



---


## **Endpoint Timings**
#### **Admin:**
* `POST /admin/song/{name}/{album}/{artist}` (532.491 ms)

#### **Analytics:**
* `GET /analytics/playlists` (82.021 ms)
* `GET /analytics/songs` (576.993 ms)

#### **Search:**
* `GET /search/playlists/{name}` (68.848 ms)
* `GET /search/songs/{name}` (461.761 ms)

#### **Users:**
* `POST /users/create` (19.972 ms)
* `DELETE /users/remove` (5453.352 ms)
* `POST /users/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_id}` (14.029 ms)
* `DELETE /users/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_id}` (3.716 ms)
* `PATCH /users/{user_id}/playlists/{playlist_id}/collaborate/{collaborator_id}`
(12.587 ms)

#### **Playlist:**
* `GET /playlists/all` (3.122 ms)
* `GET /playlists/{user_id}/all-playlists` (28.164 ms)
* `GET /playlists/{user_id}/playlists` (26.477 ms)
* `POST /playlists/{user_id}/playlists` (4.519 ms)
* `POST /playlists/{user_id}/merge/{playlist_one}/{playlist_two}` (214.965 ms)
* `DELETE /playlists/{user_id}/playlist/{playlist_id}` (385.476 ms)
* `GET /playlists/{playlist_id}/songs` (194.653 ms)
* `GET /playlists/songs/{song_id}` (11.214 ms)
* `POST /playlists/{playlist}/songs/{song_id}` (27.508 ms)
* `DELETE /playlists/{playlist_id}/songs/{song_id}` (911.373 ms)
* `POST /playlists/{user_id}/playlist/{playlist_id}/follow` (8.609 ms)
* `DELETE /playlists/{user_id}/playlist/{playlist}/unfollow` (4.763 ms)

### **Slowest Endpoints**
1. `DELETE /users/remove` (5453.352 ms)*
2. `DELETE /playlists/{playlist_id}/songs/{song_id}` (911.373 ms)
3. `GET /analytics/songs` (576.993 ms)
4. `POST /admin/song/{name}/{album}/{artist}` (532.491 ms)*
5. `GET /search/songs/{name}` (461.761 ms)




---


## **Endpoint Optimization**

### **A Note on the DELETE and POST Endpoints**
    We were unable to optimize 2 of the endpoints in our top 5,
    or at least not with Indices. These endpoints being Remove User,
    and Admin Add Song.
    
    After running an explain we found that the deleted User_id had to Cascade through the tables. Considering the fact that this user was already leaving our platform and because we didn't know how to make it any faster with indices we did not think it signifcant to improve. 
    
    Running an explain on the Admin Add Song SQL Querys showed substainally faster results than what was shown in the endpoint testing. The Curl call
    times above also include the python code which for Admin Add Song connects
    to spotify, contributing significantly to it's performance.

## **1. Top 100 Songs**
#### **Endpoint Query**
    ENDPOINT: 'GET /analytics/songs' (576.993 ms)
```sql
EXPLAIN ANALYZE
WITH song_count AS
    (
        SELECT song_id as id, COUNT(playlist_song.playlist_id) AS saves
        FROM playlist_song
        GROUP BY song_id
        ORDER BY COUNT(playlist_song.playlist_id)
        LIMIT 100  
    )
    SELECT RANK() OVER (ORDER BY saves DESC, song.title ASC) AS Rnk, song.title, album.title, artist.name, id
    FROM song_count
    LEFT JOIN song ON id = song.song_id
    LEFT JOIN artist ON song.artist_id = artist.artist_id
    LEFT JOIN album ON song.album_id = album.album_id
```
#### **Results**
``` sql
WindowAgg  (cost=60243.33..60245.33 rows=100 width=75) (actual time=462.016..462.174 rows=100 loops=1)
  ->  Sort  (cost=60243.33..60243.58 rows=100 width=67) (actual time=461.971..462.060 rows=100 loops=1)
        Sort Key: (count(playlist_song.playlist_id)) DESC, song.title
        Sort Method: quicksort  Memory: 36kB
        ->  Nested Loop Left Join  (cost=59632.18..60240.01 rows=100 width=67) (actual time=456.830..461.938 rows=100 loops=1)
              ->  Nested Loop Left Join  (cost=59631.90..60207.07 rows=100 width=54) (actual time=456.812..461.709 rows=100 loops=1)
                    ->  Hash Right Join  (cost=59631.61..60175.95 rows=100 width=44) (actual time=456.788..461.431 rows=100 loops=1)
                          Hash Cond: (song.song_id = playlist_song.song_id)
                          ->  Seq Scan on song  (cost=0.00..482.30 rows=23630 width=36) (actual time=0.017..1.940 rows=23640 loops=1)
                          ->  Hash  (cost=59630.36..59630.36 rows=100 width=16) (actual time=456.751..456.834 rows=100 loops=1)
                                Buckets: 1024  Batches: 1  Memory Usage: 13kB
                                ->  Limit  (cost=59629.11..59629.36 rows=100 width=16) (actual time=456.723..456.819 rows=100 loops=1)
                                      ->  Sort  (cost=59629.11..59687.51 rows=23357 width=16) (actual time=456.721..456.808 rows=100 loops=1)
                                            Sort Key: (count(playlist_song.playlist_id))
                                            Sort Method: top-N heapsort  Memory: 32kB
                                            ->  Finalize HashAggregate  (cost=58502.86..58736.43 rows=23357 width=16) (actual time=452.231..454.739 rows=23629 loops=1)
                                                  Group Key: playlist_song.song_id
                                                  Batches: 1  Memory Usage: 2833kB
                                                  ->  Gather  (cost=53364.32..58269.29 rows=46714 width=16) (actual time=424.271..433.665 rows=70887 loops=1)
                                                        Workers Planned: 2
                                                        Workers Launched: 2
                                                        ->  Partial HashAggregate  (cost=52364.32..52597.89 rows=23357 width=16) (actual time=411.521..414.905 rows=23629 loops=3)
                                                              Group Key: playlist_song.song_id
                                                              Batches: 1  Memory Usage: 2833kB
                                                              Worker 0:  Batches: 1  Memory Usage: 2833kB
                                                              Worker 1:  Batches: 1  Memory Usage: 2833kB
                                                              ->  Parallel Seq Scan on playlist_song  (cost=0.00..44347.88 rows=1603288 width=16) (actual time=0.047..104.365 rows=1282630 loops=3)
                    ->  Index Scan using artist_pkey on artist  (cost=0.28..0.31 rows=1 width=22) (actual time=0.002..0.002 rows=1 loops=100)
                          Index Cond: (artist_id = song.artist_id)
              ->  Index Scan using album_pkey on album  (cost=0.29..0.33 rows=1 width=29) (actual time=0.002..0.002 rows=1 loops=100)
                    Index Cond: (album_id = song.album_id)
    Planning Time: 0.605 ms
    Execution Time: 462.552 ms
```

#### **Analysis**
* Artist and Album JOINS already use Indices 
* Overwhelming majority of time spent creating song_id grouping

#### **Optimization**
```sql
CREATE MATERIALIZED VIEW IF NOT EXISTS song_saves AS
    SELECT song_id as id, COUNT(playlist_song.playlist_id) AS saves
    FROM playlist_song
    GROUP BY song_id

CREATE INDEX IF NOT EXISTS idx_song_saves ON song_saves(saves);
```

#### **Performance & Justification**
    Song popularity does not change quickly enough to justify
    calculating the count on every call. By creating a VIEW we ensure 
    the calculation is done infrequently ex.(Daily, Weekly). A job
    can then be implemented to periodically REFRESH the VIEW.

```sql
Limit  (cost=3642.52..3644.52 rows=100 width=75) (actual time=54.668..54.738 rows=100 loops=1)
  ->  WindowAgg  (cost=3642.52..4116.12 rows=23680 width=75) (actual time=54.666..54.726 rows=100 loops=1)
        ->  Sort  (cost=3642.52..3701.72 rows=23680 width=67) (actual time=54.649..54.658 rows=101 loops=1)
              Sort Key: song_saves.saves DESC, song.title
              Sort Method: quicksort  Memory: 3365kB
              ->  Hash Left Join  (cost=1370.64..1922.00 rows=23680 width=67) (actual time=21.284..41.729 rows=23629 loops=1)
                    Hash Cond: (song.album_id = album.album_id)
                    ->  Hash Left Join  (cost=962.15..1451.33 rows=23680 width=54) (actual time=16.521..31.466 rows=23629 loops=1)
                          Hash Cond: (song.artist_id = artist.artist_id)
                          ->  Hash Left Join  (cost=777.67..1204.65 rows=23680 width=44) (actual time=13.893..23.834 rows=23629 loops=1)
                                Hash Cond: (song_saves.id = song.song_id)
                                ->  Seq Scan on song_saves  (cost=0.00..364.80 rows=23680 width=16) (actual time=0.019..2.130 rows=23629 loops=1)
                                ->  Hash  (cost=482.30..482.30 rows=23630 width=36) (actual time=13.845..13.845 rows=23630 loops=1)
                                      Buckets: 32768  Batches: 1  Memory Usage: 2020kB
                                      ->  Seq Scan on song  (cost=0.00..482.30 rows=23630 width=36) (actual time=0.006..5.893 rows=23630 loops=1)
                          ->  Hash  (cost=108.10..108.10 rows=6110 width=22) (actual time=2.609..2.609 rows=6110 loops=1)
                                Buckets: 8192  Batches: 1  Memory Usage: 411kB
                                ->  Seq Scan on artist  (cost=0.00..108.10 rows=6110 width=22) (actual time=0.015..1.153 rows=6110 loops=1)
                    ->  Hash  (cost=249.33..249.33 rows=12733 width=29) (actual time=4.725..4.725 rows=12733 loops=1)
                          Buckets: 16384  Batches: 1  Memory Usage: 942kB
                          ->  Seq Scan on album  (cost=0.00..249.33 rows=12733 width=29) (actual time=0.008..1.889 rows=12733 loops=1)
Planning Time: 0.599 ms
Execution Time: 54.829 ms
```
    We can further reduce this time by adding an index on 
    the VIEW's saves column. 

```sql
Limit  (cost=192.82..272.20 rows=100 width=75) (actual time=0.759..1.910 rows=100 loops=1)
  ->  WindowAgg  (cost=192.82..18949.04 rows=23629 width=75) (actual time=0.756..1.891 rows=100 loops=1)
        ->  Incremental Sort  (cost=192.82..18535.53 rows=23629 width=67) (actual time=0.744..1.746 rows=101 loops=1)
              Sort Key: song_saves.saves DESC, song.title
              Presorted Key: song_saves.saves
              Full-sort Groups: 3  Sort Method: quicksort  Average Memory: 29kB  Peak Memory: 29kB
              ->  Nested Loop Left Join  (cost=1.16..16694.70 rows=23629 width=67) (actual time=0.072..1.650 rows=115 loops=1)
                    ->  Nested Loop Left Join  (cost=0.87..11909.46 rows=23629 width=54) (actual time=0.062..1.108 rows=115 loops=1)
                          ->  Nested Loop Left Join  (cost=0.57..9417.34 rows=23629 width=44) (actual time=0.044..0.635 rows=115 loops=1)
                                ->  Index Scan Backward using idx_song_saves on song_saves  (cost=0.29..958.57 rows=23629 width=16) (actual time=0.031..0.158 rows=115 loops=1)
                                ->  Index Scan using songs_pkey on song  (cost=0.29..0.36 rows=1 width=36) (actual time=0.003..0.003 rows=1 loops=115)
                                      Index Cond: (song_id = song_saves.id)
                          ->  Memoize  (cost=0.29..0.32 rows=1 width=22) (actual time=0.004..0.004 rows=1 loops=115)
                                Cache Key: song.artist_id
                                Cache Mode: logical
                                Hits: 7  Misses: 108  Evictions: 0  Overflows: 0  Memory Usage: 14kB
                                ->  Index Scan using artist_pkey on artist  (cost=0.28..0.31 rows=1 width=22) (actual time=0.003..0.003 rows=1 loops=108)
                                      Index Cond: (artist_id = song.artist_id)
                    ->  Memoize  (cost=0.30..0.34 rows=1 width=29) (actual time=0.004..0.004 rows=1 loops=115)
                          Cache Key: song.album_id
                          Cache Mode: logical
                          Hits: 1  Misses: 114  Evictions: 0  Overflows: 0  Memory Usage: 16kB
                          ->  Index Scan using album_pkey on album  (cost=0.29..0.33 rows=1 width=29) (actual time=0.003..0.003 rows=1 loops=114)
                                Index Cond: (album_id = song.album_id)
Planning Time: 0.831 ms
Execution Time: 2.044 ms
```

#### **Improvement**
    Initial Excecution Time: 462.552 ms
    Final Execution Time: 2.044 ms
  
## **2. Song Search**
#### **Endpoint Query**
    Endpoint: GET /search/songs/{name} (461.761 ms)
```sql
EXPLAIN ANALYZE
SELECT COALESCE(COUNT(playlist_song.playlist_id), 0) as popularity, song.song_id as id, song.title as song_title, album.title as album_title, artist.name as artist_name, duration
    FROM song
    JOIN album ON album.album_id = song.album_id
    JOIN artist ON artist.artist_id = song.artist_id
    LEFT JOIN playlist_song ON playlist_song.song_id = song.song_id
    WHERE song.title ILIKE :song_name
    GROUP BY song.song_id, song.title, album.title, artist.name, duration
    ORDER BY popularity
```

#### **Results**
```sql
Sort  (cost=76542.45..76543.26 rows=322 width=71) (actual time=602.161..602.164 rows=2 loops=1)
  Sort Key: (COALESCE(count(playlist_song.playlist_id), '0'::bigint))
  Sort Method: quicksort  Memory: 25kB
  ->  GroupAggregate  (cost=76521.79..76529.04 rows=322 width=71) (actual time=602.121..602.158 rows=2 loops=1)
        Group Key: song.song_id, album.title, artist.name
        ->  Sort  (cost=76521.79..76522.60 rows=322 width=71) (actual time=602.083..602.098 rows=333 loops=1)
              Sort Key: song.song_id, album.title, artist.name
              Sort Method: quicksort  Memory: 65kB
              ->  Nested Loop  (cost=541.99..76508.38 rows=322 width=71) (actual time=20.668..601.802 rows=333 loops=1)
                    ->  Nested Loop  (cost=541.69..76475.49 rows=322 width=61) (actual time=20.652..601.582 rows=333 loops=1)
                          ->  Hash Right Join  (cost=541.40..76442.59 rows=322 width=48) (actual time=20.618..601.172 rows=333 loops=1)
                                Hash Cond: (playlist_song.song_id = song.song_id)
                                ->  Seq Scan on playlist_song  (cost=0.00..65926.60 rows=3799160 width=16) (actual time=0.076..251.364 rows=3799160 loops=1)
                                ->  Hash  (cost=541.38..541.38 rows=2 width=40) (actual time=15.933..15.933 rows=2 loops=1)
                                      Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                      ->  Seq Scan on song  (cost=0.00..541.38 rows=2 width=40) (actual time=1.594..15.925 rows=2 loops=1)
                                            Filter: (title ~~* 'california girls'::text)
                                            Rows Removed by Filter: 23628
                          ->  Memoize  (cost=0.30..8.31 rows=1 width=29) (actual time=0.001..0.001 rows=1 loops=333)
                                Cache Key: song.album_id
                                Cache Mode: logical
                                Hits: 331  Misses: 2  Evictions: 0  Overflows: 0  Memory Usage: 1kB
                                ->  Index Scan using album_pkey on album  (cost=0.29..8.30 rows=1 width=29) (actual time=0.014..0.015 rows=1 loops=2)
                                      Index Cond: (album_id = song.album_id)
                    ->  Memoize  (cost=0.29..8.31 rows=1 width=22) (actual time=0.000..0.000 rows=1 loops=333)
                          Cache Key: song.artist_id
                          Cache Mode: logical
                          Hits: 331  Misses: 2  Evictions: 0  Overflows: 0  Memory Usage: 1kB
                          ->  Index Scan using artist_pkey on artist  (cost=0.28..8.30 rows=1 width=22) (actual time=0.011..0.011 rows=1 loops=2)
                                Index Cond: (artist_id = song.artist_id)
Planning Time: 0.940 ms
Execution Time: 602.263 ms
```
#### **Analysis**
* The JOIN for playlist_song is located within a double nested loop
* There is a Seq Scan within the JOIN that required song_id
* There is a Seq Scan also within this loop for song that filters
every row in that table by title

#### **Optimization**
```sql
CREATE INDEX idx_playlist_track ON playlist_song(song_id);
```

#### **Performance & Justification**
    song_id is referenced within the nested loops
    and as such any improvment to song_id calls
    should significantly impact the time. Title
    is used in a string comparison and as such when 
    tested the Index was found to be in effective. 

```sql
Sort  (cost=1849.30..1850.10 rows=322 width=71) (actual time=21.609..21.613 rows=2 loops=1)
  Sort Key: (COALESCE(count(playlist_song.playlist_id), '0'::bigint))
  Sort Method: quicksort  Memory: 25kB
  ->  GroupAggregate  (cost=1828.64..1835.88 rows=322 width=71) (actual time=21.501..21.591 rows=2 loops=1)
        Group Key: song.song_id, album.title, artist.name
        ->  Sort  (cost=1828.64..1829.44 rows=322 width=71) (actual time=21.407..21.444 rows=333 loops=1)
              Sort Key: song.song_id, album.title, artist.name
              Sort Method: quicksort  Memory: 65kB
              ->  Nested Loop Left Join  (cost=6.25..1815.22 rows=322 width=71) (actual time=3.848..21.124 rows=333 loops=1)
                    ->  Nested Loop  (cost=0.57..574.58 rows=2 width=63) (actual time=3.728..20.198 rows=2 loops=1)
                          ->  Nested Loop  (cost=0.29..557.98 rows=2 width=53) (actual time=3.685..20.146 rows=2 loops=1)
                                ->  Seq Scan on song  (cost=0.00..541.38 rows=2 width=40) (actual time=3.624..20.078 rows=2 loops=1)
                                      Filter: (title ~~* 'california girls'::text)
                                      Rows Removed by Filter: 23628
                                ->  Index Scan using album_pkey on album  (cost=0.29..8.30 rows=1 width=29) (actual time=0.027..0.027 rows=1 loops=2)
                                      Index Cond: (album_id = song.album_id)
                          ->  Index Scan using artist_pkey on artist  (cost=0.28..8.30 rows=1 width=22) (actual time=0.022..0.022 rows=1 loops=2)
                                Index Cond: (artist_id = song.artist_id)
                    ->  Bitmap Heap Scan on playlist_song  (cost=5.69..618.70 rows=162 width=16) (actual time=0.072..0.386 rows=166 loops=2)
                          Recheck Cond: (song_id = song.song_id)
                          Heap Blocks: exact=332
                          ->  Bitmap Index Scan on idx_playlist_track  (cost=0.00..5.64 rows=162 width=0) (actual time=0.032..0.032 rows=166 loops=2)
                                Index Cond: (song_id = song.song_id)
Planning Time: 1.488 ms
Execution Time: 21.784 ms
```

#### **Improvement**
    Initial Execution Time: 602.263 ms
    Final Execution Time: 21.784 ms

## **3. Delete Song From Playlist **
#### **Endpoint Query**
    Endpoint: `DELETE /playlists/{playlist_id}/songs/{song_id}` (911.373 ms)
1. 
```sql
EXPLAIN ANALYZE
SELECT 1
FROM playlist_song
WHERE playlist_song.playlist_id = :playlist_id AND playlist_song.song_id = :song_id
```

2. 
```sql
EXPLAIN ANALYZE
SELECT 1
FROM playlist
WHERE (:user_id = (SELECT user_id
    FROM playlist
    WHERE playlist_id = :playlist_id) 
    OR :user_id = (SELECT user_id 
    FROM playlist_collaborator
    WHERE playlist_id = :playlist_id))
```

3. 
```sql
EXPLAIN ANALYZE
DELETE FROM playlist_song
        WHERE playlist_id = :playlist_id AND song_id = :song_id  
```

#### **Results**
1. 
```sql
Bitmap Heap Scan on playlist_song  (cost=5.65..619.07 rows=1 width=4) (actual time=0.877..0.879 rows=1 loops=1)
  Recheck Cond: (song_id = '7079'::bigint)
  Filter: (playlist_id = '126697'::bigint)
  Rows Removed by Filter: 152
  Heap Blocks: exact=151
  ->  Bitmap Index Scan on idx_playlist_track  (cost=0.00..5.64 rows=162 width=0) (actual time=0.050..0.050 rows=153 loops=1)
        Index Cond: (song_id = '7079'::bigint)
Planning Time: 0.337 ms
Execution Time: 0.906 ms
```

2. 
```sql
Result  (cost=12.62..2495.68 rows=126706 width=4) (actual time=0.109..29.805 rows=126706 loops=1)
  One-Time Filter: (('4000'::bigint = $0) OR ('4000'::bigint = $1))
  InitPlan 1 (returns $0)
    ->  Index Scan using playlist_pkey on playlist playlist_1  (cost=0.29..8.31 rows=1 width=8) (actual time=0.083..0.087 rows=1 loops=1)
          Index Cond: (playlist_id = '126697'::bigint)
  InitPlan 2 (returns $1)
    ->  Index Only Scan using playlist_collaborators_pkey on playlist_collaborator  (cost=0.29..4.30 rows=1 width=8) (never executed)
          Index Cond: (playlist_id = '126697'::bigint)
          Heap Fetches: 0
  ->  Seq Scan on playlist  (cost=0.01..2483.07 rows=126706 width=0) (actual time=0.010..12.790 rows=126706 loops=1)
Planning Time: 0.203 ms
Execution Time: 38.128 ms
```

3. 
```sql
Delete on playlist_song  (cost=5.65..619.07 rows=0 width=0) (actual time=0.294..0.295 rows=0 loops=1)
  ->  Bitmap Heap Scan on playlist_song  (cost=5.65..619.07 rows=1 width=6) (actual time=0.262..0.263 rows=1 loops=1)
        Recheck Cond: (song_id = '7079'::bigint)
        Filter: (playlist_id = '126697'::bigint)
        Rows Removed by Filter: 152
        Heap Blocks: exact=151
        ->  Bitmap Index Scan on idx_playlist_track  (cost=0.00..5.64 rows=162 width=0) (actual time=0.030..0.031 rows=153 loops=1)
              Index Cond: (song_id = '7079'::bigint)
Planning Time: 0.153 ms
Execution Time: 0.367 ms
```
#### **Analysis**
* The Delete Song endpoint contains 3 sql calls, the first 2 are error checks, the 3rd deletes the song. 
* The 1st and 3rd calls benefit from our previous optimization, the idx_playlist_tracks index. 



#### **Optimization**
1. 
```sql
CREATE INDEX idx_playlist_track ON playlist_song(song_id);
CREATE INDEX idx_playlist_id ON playlist_song(playlist_id);
```
    Our previous optimization to add a playlist_track index continues
    to help with this endpoint. In addition a playlist_id index also
    ended up being useful here. However the most significant time was
    in checking the user's permissions which could not be optimized.

#### **Performance & Justification**
1. 
```sql 
Index Scan using idx_playlist_id on playlist_song  (cost=0.43..9.05 rows=1 width=4) (actual time=0.029..0.036 rows=1 loops=1)
  Index Cond: (playlist_id = '126697'::bigint)
  Filter: (song_id = '17337'::bigint)
  Rows Removed by Filter: 25
Planning Time: 0.123 ms
Execution Time: 0.062 ms 
```

2. 
```sql
Result  (cost=12.62..2495.68 rows=126706 width=4) (actual time=0.062..30.060 rows=126706 loops=1)
  One-Time Filter: (('4000'::bigint = $0) OR ('4000'::bigint = $1))
  InitPlan 1 (returns $0)
    ->  Index Scan using playlist_pkey on playlist playlist_1  (cost=0.29..8.31 rows=1 width=8) (actual time=0.042..0.044 rows=1 loops=1)
          Index Cond: (playlist_id = '126697'::bigint)
  InitPlan 2 (returns $1)
    ->  Index Only Scan using playlist_collaborators_pkey on playlist_collaborator  (cost=0.29..4.30 rows=1 width=8) (never executed)
          Index Cond: (playlist_id = '126697'::bigint)
          Heap Fetches: 0
  ->  Seq Scan on playlist  (cost=0.01..2483.07 rows=126706 width=0) (actual time=0.009..12.704 rows=126706 loops=1)
Planning Time: 0.206 ms
Execution Time: 38.414 ms
```

3. 
```sql
Delete on playlist_song  (cost=13.04..21.66 rows=0 width=0) (actual time=0.132..0.133 rows=0 loops=1)
  InitPlan 1 (returns $0)
    ->  Index Scan using playlist_pkey on playlist  (cost=0.29..8.31 rows=1 width=8) (actual time=0.023..0.025 rows=1 loops=1)
          Index Cond: (playlist_id = '126697'::bigint)
  InitPlan 2 (returns $1)
    ->  Index Only Scan using playlist_collaborators_pkey on playlist_collaborator  (cost=0.29..4.30 rows=1 width=8) (never executed)
          Index Cond: (playlist_id = '126697'::bigint)
          Heap Fetches: 0
  ->  Result  (cost=0.43..9.05 rows=1 width=6) (actual time=0.044..0.050 rows=1 loops=1)
        One-Time Filter: (('4000'::bigint = $0) OR ('4000'::bigint = $1))
        ->  Index Scan using idx_playlist_id on playlist_song  (cost=0.43..9.05 rows=1 width=6) (actual time=0.013..0.018 rows=1 loops=1)
              Index Cond: (playlist_id = '126697'::bigint)
              Filter: (song_id = '17337'::bigint)
              Rows Removed by Filter: 25
Planning Time: 0.214 ms
Execution Time: 0.179 ms
```

#### **Improvement**
    Initial Execution Time(Sum): 39.401
    Final Execution Time(Sum): 38.655
