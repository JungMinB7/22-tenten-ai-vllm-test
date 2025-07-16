import pytest
from services.bot_chats_service import BotChatsService
from types import SimpleNamespace

@pytest.fixture
def fake_app():
    # app.state.model은 사용하지 않으므로 더미 객체로 대체
    app = SimpleNamespace()
    app.state = SimpleNamespace()
    app.state.model = None
    return app

@pytest.fixture
def service(fake_app):
    return BotChatsService(fake_app)

def test_memory_creation_and_isolation(service):
    # 서로 다른 stream_id에 대해 독립적인 메모리 인스턴스가 생성되는지 확인
    mem1 = service.get_memory('stream1')
    mem2 = service.get_memory('stream2')
    assert mem1 is not mem2

def test_add_and_get_recent_messages(service):
    stream_id = 'test_stream'
    # 6개 메시지 추가 (최대 5개만 저장되어야 함)
    for i in range(6):
        service.add_message_to_memory(stream_id, 'user', f'msg{i}')
    recent = service.get_recent_messages(stream_id)
    assert len(recent) == 5
    # 가장 오래된 메시지는 사라지고, 최근 5개만 남아야 함
    assert recent[0]['content'] == 'msg1'
    assert recent[-1]['content'] == 'msg5'

def test_delete_memory(service):
    stream_id = 'delete_stream'
    service.add_message_to_memory(stream_id, 'user', 'hello')
    assert stream_id in service.memory_dict
    service.delete_memory(stream_id)
    assert stream_id not in service.memory_dict 