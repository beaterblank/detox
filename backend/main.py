import uvicorn
import logging

from typing import List
from pydantic import BaseModel
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	exc_str = f'{exc}'.replace('\n', ' ').replace('   ', ' ')
	logging.error(f"{request}: {exc_str}")
	content = {'status_code': 10422, 'message': exc_str, 'data': None}
	return JSONResponse(content=content, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class Thumbnail(BaseModel):
    href:str
    text:str

def get_video_details(url):
    return {
        "title":"",
        "description":"",
        "video_length":0,# in seconds
        "views":0,
        "captions":{
            "en":"",
        },
        "upload_date":"",
        "channel_name":"",
        "subscriber_count":0,
        "likes":0,
    }

@app.post("/")
async def get_data(thumbnail:Thumbnail):
    return thumbnail

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
