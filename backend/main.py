"""
Filter youtube videos on your feed
Based on the the following variables

date uploaded
likes
view count
video_length
always allow or disallow certain channels
allow or disallow certain topics using 
zero shot classification with BERT

"""
import time
import os
import uvicorn
import logging
import random
import redis


from pathlib import Path
from typing import List, Callable
from fastapi.routing import APIRoute
from fastapi import APIRouter, Response
from fastapi.responses import JSONResponse
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError

from models import Thumbnail
from youtube import get_video_details
from youtube import filter_video
from youtube import get_config

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# TODO add Redis support
REDIS_HOST = os.environ.get("REDIS_HOST","172.17.0.2")
REDIS_PORT = os.environ.get("REDIS_PORT",6379)
REDIS_USERNAME = os.environ.get("REDIS_USERNAME","default")
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD","secret")

"""
redis_cache = redis.Redis(
    host=REDIS_HOST, port=REDIS_PORT,
    username=REDIS_USERNAME, 
    password=REDIS_PASSWORD, 
    ssl=True,
    ssl_certfile="./redis_user.crt",
    ssl_keyfile="./redis_user_private.key",
    ssl_ca_certs="./redis_ca.pem",
)
"""
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)

@app.post("/")
async def get_data(thumbnail:Thumbnail):
    config = get_config()
    start =  time.time()
    video_info = get_video_details(thumbnail.href)
    if video_info == {}:
        print("video details failed to extact")
        return True
    out = filter_video(video_info,config)
    end = time.time()
    print(f'{thumbnail.href}:{out}:{end-start} s')
    return out

if __name__ == "__main__":
    uvicorn.run(f"{Path(__file__).stem}:app", host='0.0.0.0', port=8000, workers=5)
