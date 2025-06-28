# import pytest
# from redis.exceptions import RedisError, ConnectionError
# from repository.redis_repo import RedisRepo

# @pytest.mark.asyncio
# async def test_redis_instance_connection():
#     try:
#         redis1 = await RedisRepo.get_instance()
#         redis2 = await RedisRepo.get_instance()

#         # 싱글톤 검증
#         assert redis1 is redis2

#         # 연결 확인
#         pong = await redis1.ping()
#         assert pong is True

#         # config 확인 (옵션)
#         config = await redis1.config_get("notify-keyspace-events")
#         assert config.get("notify-keyspace-events") == "Ex"

#     except (ConnectionError, RedisError) as e:
#         pytest.fail(f"Redis 연결에 실패했습니다: {e}")