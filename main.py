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

@app.get("/items/{item_id}")
def test_read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.post("/testing/{item_id}")
def test_function(num: int): # parameters show up in docs
    print('testing output') # prints show up in render log
    return {"item_id": 333} # returns act as responses

@app.post("/user/{user_id}/playlist/create_playlist")
def create_playlist(user_id: int, playlist_name: str = None):
    
    with engine.begin() as connection:

        # insert a new playlist into table
        sql_to_execute = 'INSERT INTO playlist (user_id) VALUES (:user_id)'
        connection.execute(sqlalchemy.text(sql_to_execute), {'user_id': user_id})

        sql_to_execute = "INSERT INTO public.user (first_name) VALUES ('fuck off')"
        connection.execute(sqlalchemy.text(sql_to_execute))

        
    
        # update the playlist with a name if one was provided
    
    # return playlist_id ???

    pass

def test():

    print('fuck')

    # Test the connection
    with engine.connect() as connection:
        # sql_to_execute = "select first_name from public.user"

        # sql_to_execute = "INSERT INTO public.user (first_name) values ('whatup')"
        # connection.execute(sqlalchemy.text(sql_to_execute))

        print("Done connecting with the Supabase database!")

if __name__=="__main__":
    create_playlist(9)