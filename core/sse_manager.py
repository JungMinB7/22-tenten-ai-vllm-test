from asyncio import Queue
from typing import Dict

class SSEManager:
    def __init__(self):
        self.connections: Dict[str, Queue] = {}

    async def connect(self, client_id: str) -> Queue:
        """새로운 클라이언트 연결 및 큐 생성"""
        queue = Queue()
        self.connections[client_id] = queue
        return queue

    def disconnect(self, client_id: str):
        """클라이언트 연결 종료"""
        if client_id in self.connections:
            del self.connections[client_id]

    async def broadcast(self, message: str):
        """모든 연결된 클라이언트에게 메시지 브로드캐스트"""
        for queue in self.connections.values():
            await queue.put(message)

# 싱글턴 인스턴스
sse_manager = SSEManager() 