import pytest
from service.db_service import ActiveList
from model.models import TokenResponse
from utils import config
import uuid

@pytest.mark.asyncio
async def test_active_add_and_exists(fake_redis):
    active_list = ActiveList(fake_redis)
    token = TokenResponse(uuid=str(uuid.uuid4()), status="active")

    await active_list.add_to_active(token)

    # 세트에 있는지
    in_set = await fake_redis.sismember(config.ACTIVE_SET_KEY, token.uuid)
    assert in_set == 1

    # 토큰 키가 존재하는지
    exists = await active_list.exists(token.uuid)
    assert exists is True

@pytest.mark.asyncio
async def test_active_remove_and_count(fake_redis):
    active_list = ActiveList(fake_redis)
    token = TokenResponse(uuid=str(uuid.uuid4()), status="active")

    await active_list.add_to_active(token)
    count_before = await active_list.count()
    assert count_before == 1

    await active_list.remove(token.uuid)
    count_after = await active_list.count()
    assert count_after == 0

    exists = await active_list.exists(token.uuid)
    assert exists is False

@pytest.mark.asyncio
async def test_active_get_members(fake_redis):
    active_list = ActiveList(fake_redis)
    token1 = TokenResponse(uuid=str(uuid.uuid4()), status="active")
    token2 = TokenResponse(uuid=str(uuid.uuid4()), status="active")

    await active_list.add_to_active(token1)
    await active_list.add_to_active(token2)

    members = await active_list.get_members()
    assert token1.uuid in members
    assert token2.uuid in members
