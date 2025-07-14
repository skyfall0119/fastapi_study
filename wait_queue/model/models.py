from pydantic import BaseModel
from enum import Enum

class TokenResponse(BaseModel):
    uuid: str
    status: str 
    exp:int = 100000