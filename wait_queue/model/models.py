from pydantic import BaseModel

class TokenResponse(BaseModel):
    uuid: str
    status: str # 'wait' | 'active'
