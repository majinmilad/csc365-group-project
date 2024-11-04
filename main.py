from typing import Optional
from fastapi import FastAPI
app = FastAPI()

import sqlalchemy
from sqlalchemy import create_engine

DATABASE_URL = "postgresql://postgres.nqueeijmuxlkmckrcxst:weresocookedbro@aws-0-us-west-1.pooler.supabase.com:6543/postgres"

engine = create_engine(DATABASE_URL)


@app.get("/")
async def root():
    return {"message": "Changing this message! Whoo!"}


@app.post("/user/{user_id}/playlist/create_playlist")
def create_playlist(user_id: int, playlist_name: str = None):
    
    with engine.begin() as connection:

        # insert a new playlist into table
        sql_to_execute = 'INSERT INTO playlist (user_id) VALUES (:user_id) RETURNING playlist_id'
        result = connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': user_id})

        playlist_id = result.scalar()

        # update the playlist with a name if one was provided
        if playlist_name is not None:
            sql_to_execute = 'UPDATE playlist SET playlist_name = :playlist_name WHERE playlist_id = :playlist_id'
            connection.execute(sqlalchemy.text(sql_to_execute), {'playlist_name': playlist_name, 'playlist_id': playlist_id})

    return playlist_id


@app.post("/user/{user_id}/playlist/add_song")
def add_song_to_playlist(user_id: int, song_id: int, playlist_id: int):

    with engine.begin() as connection:

        # insert a new playlist into table
        sql_to_execute = 'INSERT INTO playlist_song (song_id, playlist_id) VALUES (:song_id, :playlist_id)'
        connection.execute(sqlalchemy.text(sql_to_execute), {'song_id': song_id, 'playlist_id': playlist_id})
    
    return "Ok"


if __name__=="__main__":
    # create_playlist(user_id=24, playlist_name='dope ass playlist')
    # add_song_to_playlist(3, 4, 5)
    pass