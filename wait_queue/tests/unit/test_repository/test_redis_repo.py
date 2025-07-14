import pytest
from redis.exceptions import RedisError, ConnectionError
import repository.redis_repo as redis_repo

@pytest.mark.asyncio
async def test_redis_instance_connection():
    try:
        await redis_repo.init_redis()
        redis1 = redis_repo.get_redis_sync()
        redis2 = redis_repo.get_redis_sync()

        # 싱글톤 검증
        assert redis1 is redis2

        # 연결 확인
        pong = await redis1.ping()
        assert pong is True

        # config 확인 (옵션)
        config = await redis1.config_get("notify-keyspace-events")
        redis_option = config.get("notify-keyspace-events")
        assert set(redis_option) == set("Ex")

    except (ConnectionError, RedisError) as e:
        pytest.fail(f"Redis 연결에 실패했습니다: {e}")