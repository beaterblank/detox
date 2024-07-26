from pydantic import BaseModel

class Thumbnail(BaseModel):
    href:str
    text:str
