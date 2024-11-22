from fastapi import FastAPI, exceptions
from fastapi.responses import JSONResponse
from pydantic import ValidationError
#add api endpoints here and down there
from src.api import search, users
import json
import logging
import sys
from starlette.middleware.cors import CORSMiddleware

description = """
Playlist Mixer TypeShit
"""

app = FastAPI(
    title="Playlist Mixer",
    description=description,
    version="0.0.1",
    terms_of_service="null",
    contact={
        "name": "Edson Munoz",
        "email": "emunoz23@calpoly.edu",
    },
)

origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

#add api points here 
app.include_router(search.router)
app.include_router(users.router)


@app.exception_handler(exceptions.RequestValidationError)
@app.exception_handler(ValidationError)
async def validation_exception_handler(request, exc):
    logging.error(f"The client sent invalid data!: {exc}")
    exc_json = json.loads(exc.json())
    response = {"message": [], "data": None}
    for error in exc_json:
        response['message'].append(f"{error['loc']}: {error['msg']}")

    return JSONResponse(response, status_code=422)

@app.get("/")
async def root():
    return {"message": "Welcome to Hell"}
