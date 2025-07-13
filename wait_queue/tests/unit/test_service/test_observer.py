import pytest
from unittest.mock import AsyncMock, MagicMock
from service.observer import WaitQueueObserver
from model.models import TokenResponse
from fastapi import WebSocket
from utils import config

@pytest.mark.asyncio
async def test_attach_valid_token(fake_redis):
    observer = WaitQueueObserver(redis=fake_redis)

    # Token과 WebSocket 준비
    token = TokenResponse(uuid="abc-123", status="wait")
    fake_ws = AsyncMock(spec=WebSocket)

    # 토큰 검증 성공하도록 모킹
    observer.db_service.wait_queue.validate = AsyncMock(return_value=True)

    result = await observer.attach(token, fake_ws)

    assert result is True
    # fake_ws.accept.assert_awaited_once()
    assert token.uuid in observer.ws_dict

@pytest.mark.asyncio
async def test_attach_invalid_token_closes_socket(fake_redis):
    observer = WaitQueueObserver(redis=fake_redis)

    token = TokenResponse(uuid="abc-456", status="wait")
    fake_ws = AsyncMock(spec=WebSocket)
    observer.db_service.wait_queue.validate = AsyncMock(return_value=False)

    result = await observer.attach(token, fake_ws)

    assert result is False
    fake_ws.close.assert_awaited_once()
    assert token.uuid not in observer.ws_dict

@pytest.mark.asyncio
async def test_detach_removes_socket(fake_redis):
    observer = WaitQueueObserver(redis=fake_redis)
    observer.ws_dict = {"abc-123": AsyncMock()}

    await observer.detach("abc-123")
    assert "abc-123" not in observer.ws_dict

@pytest.mark.asyncio
async def test_promote_and_notify_sends_message(fake_redis):
    observer = WaitQueueObserver(redis=fake_redis)

    # 등록된 토큰
    token = TokenResponse(uuid="abc-789", status="wait")
    mock_ws = AsyncMock()
    observer.ws_dict[token.uuid] = mock_ws

    observer.db_service.promote_to_active = AsyncMock(return_value=token)

    await observer._promote_and_notify()

    mock_ws.send_json.assert_awaited_once()
    mock_ws.close.assert_awaited_once()
    assert token.uuid not in observer.ws_dict

@pytest.mark.asyncio
async def test_notify_wait_number_sends_position(fake_redis):
    observer = WaitQueueObserver(redis=fake_redis)
    observer.ws_dict = {
        "user1": AsyncMock(),
        "user2": AsyncMock()
    }

    observer.db_service.wait_queue.get_all_waiting = AsyncMock(return_value=["user1", "user2"])

    await observer._notify_wait_number()

    observer.ws_dict["user1"].send_json.assert_awaited_with({"status": "wait", "position": 1})
    observer.ws_dict["user2"].send_json.assert_awaited_with({"status": "wait", "position": 2})

@pytest.mark.asyncio
async def test_is_there_active_room(fake_redis):
    observer = WaitQueueObserver(redis=fake_redis)

    observer.db_service.active_set.count = AsyncMock(return_value=2)
    result = await observer._is_there_active_room()

    assert result == config.MAX_ACTIVE_SET - 2
