from fastapi import APIRouter
import spotify_auth
import requests
import json

router = APIRouter(
    prefix="/search",
    tags=['search']
)

@router.get("/artist/{artist_name}")
def search_for_artists(artist_name: str = None):
    token = spotify_auth.get_spotify_token()
    url = "https://api.spotify.com/v1/search"
    headers = spotify_auth.get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=5"

    query_url = url + query
    response = requests.get(query_url, headers=headers)
    json_result = json.loads(response.content)
    artist_list = []
    for artist in json_result['artists']['items']:
        artist_list.append(
            {
                'id': artist['id'],
                'name': artist['name'],
                'type': artist['type'],
                'genres': artist['genres'],
                'popularity': artist['popularity'],
                'followers': artist['followers']['total']
            }
        )
    return artist_list

@router.get("/song/{song_name}")
def search_for_songs(song_name: str = None):
    token = spotify_auth.get_spotify_token()
    url = "https://api.spotify.com/v1/search"
    headers = spotify_auth.get_auth_header(token)
    query = f"?q={song_name}&type=track&limit=5"

    query_url = url + query
    response = requests.get(query_url, headers=headers)
    json_result = json.loads(response.content)
    song_list = []
    for song in json_result['tracks']['items']:
        song_list.append(
            {
                'id': song['id'],
                'name': song['name'],
                'type': song['type'],
                'track': song['track_number'],
                'album': song['album']['name'],
                'artist': song['artists'][0]['name'],
                'popularity': song['popularity'],
                'duration': song['duration_ms']
            }
        )
    return song_list