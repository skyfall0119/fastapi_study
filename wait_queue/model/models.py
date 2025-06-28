from pydantic import BaseModel
from enum import Enum, auto

class TokenResponse(BaseModel):
    uuid: str
    status: str # 'wait' | 'active' Enum.name 으로 관리


class enuff(Enum):
    WAIT = 0
    ACTIVE = 1
