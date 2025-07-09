from fastapi import Request, HTTPException


async def get_validated_token(request: Request):
    auth = request.headers.get("Authorization")
    if not auth:
        raise HTTPException(status_code=401, detail="Missing token")
    token = auth.replace("Bearer ", "").strip()
    # TODO: validate token here (signature, expiration, etc.)
    return token