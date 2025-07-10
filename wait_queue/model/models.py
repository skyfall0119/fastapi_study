from pydantic import BaseModel
from enum import Enum, auto

class TokenResponse(BaseModel):
    uuid: str
    status: str 
    exp:int = 0


class enuff(Enum):
    WAIT = 0
    ACTIVE = 1
