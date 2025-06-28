# import pytest
# import asyncio
# import fakeredis.aioredis
# from service.db_service import DbService
# from model.models import TokenResponse
# from utils import config

# @pytest.fixture
# async def fake_redis():
#     redis = await fakeredis.aioredis.FakeRedis()
#     await redis.flushall()
#     return redis

# @pytest.fixture
# async def db_service(fake_redis):
#     return await DbService(fake_redis)


# @pytest.mark.asyncio
# async def test_token_creation(db_service: DbService):
#     token = await db_service.create_token()
#     assert token.status == config.TOKEN_WAIT
#     assert isinstance(token.uuid, str)

#     stored_tokens = await db_service.wait_queue.get_all_waiting()
#     assert token.uuid in stored_tokens