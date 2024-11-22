from dotenv import load_dotenv
import os
import base64
import requests
import json
import datetime

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_spotify_token():
    credentials = f"{client_id}:{client_secret}"
    credentials_b64 = base64.b64encode(credentials.encode())
    token_url = "https://accounts.spotify.com/api/token"
    method = "POST"
    token_data = {
        "grant_type": "client_credentials"
    }
    token_header = {
        "Authorization": f"Basic {credentials_b64.decode()}"
    }
    response = requests.post(token_url, data=token_data, headers=token_header).json()
    now = datetime.datetime.now()
    token = response['access_token']
    expires_in = response['expires_in']
    expires = now + datetime.timedelta(seconds=expires_in)
    expired = now > expires
    return token
   
def get_auth_header(token):
    return {"Authorization": "Bearer " + token}