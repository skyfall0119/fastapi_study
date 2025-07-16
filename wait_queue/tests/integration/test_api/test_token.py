# import pytest
# from httpx import AsyncClient
# from main import app 
# from utils import config
# from httpx import ASGITransport

# ASGITransport(app=app) 은 FastAPI 서버를 내부적으로 호출할 수 있게 해줌.
## redis 만 띄웠을 때
# @pytest.mark.asyncio
# async def test_generate_token_async():
#     async with AsyncClient(
#         transport=ASGITransport(app=app),
#         base_url="http://test"
#     ) as client:
#         response = await client.post("/token")
#         assert response.status_code == 200

#         data = response.json()
#         assert "uuid" in data
#         assert data["status"] == config.TOKEN_WAIT





import pytest
from httpx import AsyncClient
from utils.util import decode_token

@pytest.mark.asyncio
async def test_generate_token():
    async with AsyncClient(base_url="http://localhost:8000") as client:
        response = await client.post("/token/")
        assert response.status_code == 200

        data = response.json()

        assert "access_token" in data
        ## decode jwt token
        decoded = decode_token(data['access_token'])
        print(decoded)
        assert "uuid" in decoded
        assert "status" in decoded
        assert "exp" in decoded
        assert decoded["status"] == "wait"
        
