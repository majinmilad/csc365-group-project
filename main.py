from typing import Optional

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Changing this message! Whoo!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}

@app.post("/testing/{item_id}")
def read_item(num: int): # parameters show up in docs
    print('testing output') # prints show up in render log
    return {"item_id": 333} # returns act as responses

@app.post("/user/{user_id}/playlist/create_playlist")
def create_playlist(user_id: int):
    # insert playlist into table
    
    # return playlist_id ???

    pass