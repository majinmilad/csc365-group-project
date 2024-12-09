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
1. `DELETE /users/remove` (5453.352 ms)
2. `DELETE /playlists/{playlist_id}/songs/{song_id}` (911.373 ms)
3. `GET /analytics/songs` (576.993 ms)
4. `POST /admin/song/{name}/{album}/{artist}` (532.491 ms)
5. `GET /search/songs/{name}` (461.761 ms)

## **Endpoint Analysis and Improvement**
### **1. Delete User Account**
`DELETE /users/remove` (5453.352 ms)

### **2. Remove Song From Playlist**
`DELETE /playlists/{playlist_id}/songs/{song_id}` (911.373 ms)

### **3. Top 100 Songs**
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
```
    Planning Time: 0.605 ms
    Execution Time: 462.552 ms

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

SELECT RANK() OVER (ORDER BY saves DESC, song.title ASC) AS Rnk, song.title, album.title, artist.name, id
FROM song_saves
LEFT JOIN song ON id = song.song_id
LEFT JOIN artist ON song.artist_id = artist.artist_id
LEFT JOIN album ON song.album_id = album.album_id
LIMIT 100
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
