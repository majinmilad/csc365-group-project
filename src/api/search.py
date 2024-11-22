from fastapi import APIRouter, Depends, Request
import spotify_auth
import requests
import json

router = APIRouter(
    prefix="/search",
    tags=['search']
)

@router.get("/search/{artist_name}")
def search_for_artists(artist_name: str = None):
    token = spotify_auth.get_spotify_token()
    url = "https://api.spotify.com/v1/search"
    headers = spotify_auth.get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1"

    query_url = url + query
    response = requests.get(query_url, headers=headers)
    json_result = json.loads(response.content)
    artist_info = {
        'id': json_result['artists']['items'][0]['id'],
        'name': json_result['artists']['items'][0]['name'],
        'type': json_result['artists']['items'][0]['type'],
        'genres': json_result['artists']['items'][0]['genres'],
        'popularity': json_result['artists']['items'][0]['popularity'],
        'followers': json_result['artists']['items'][0]['followers']['total']
    }
    return artist_info

@router.get("/search/{song_name}")
def search_for_songs(song_name: str = None):
    token = spotify_auth.get_spotify_token()
    url = "https://api.spotify.com/v1/search"
    headers = spotify_auth.get_auth_header(token)
    query = f"?q={song_name}&type=track&limit=1"

    query_url = url + query
    response = requests.get(query_url, headers=headers)
    json_result = json.loads(response.content)
    song_info = {
        'id': json_result['tracks']['items'][0]['id'],
        'name': json_result['tracks']['items'][0]['name'],
        'type': json_result['tracks']['items'][0]['type'],
        'track': json_result['tracks']['items'][0]['track_number'],
        'album': json_result['tracks']['items'][0]['album']['name'],
        'artist': json_result['tracks']['items'][0]['artists'][0]['name'],
        'popularity': json_result['tracks']['items'][0]['popularity'],
        'duration' :json_result['tracks']['items'][0]['duration_ms']
    }
    return song_info