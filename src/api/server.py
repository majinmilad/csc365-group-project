from fastapi import FastAPI, exceptions, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError
#add api endpoints here and down there
from src.api import admin, analytics, search, users, playlists
import json
import logging
from starlette.middleware.cors import CORSMiddleware
import time

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
app.include_router(admin.router)
app.include_router(analytics.router)
app.include_router(search.router)
app.include_router(users.router)
app.include_router(playlists.router)


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

@app.middleware("http")
async def measure_runtime(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    print(f"Endpoint {request.url.path} took {process_time*1000:.4f} milliseconds")
    return response
