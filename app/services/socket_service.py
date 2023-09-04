from typing import Dict, Any, Set
from fastapi.websockets import WebSocket


TMessagePayload = Any
TActiveChatConnections = Dict[int, Set[WebSocket]]
TActiveUserConnections = Dict[int, Set[WebSocket]]


class SocketService:
    def __init__(self):
        self.active_chat_connections: TActiveChatConnections = {}
        self.active_user_connections: TActiveUserConnections = {}

    def _get_connection_dict_by_type(self, connection_type: str = 'user'):
        if connection_type == 'user':
            return self.active_user_connections
        return self.active_chat_connections

    async def connect(self, websocket: WebSocket, instance_id: int, connection_type: str = 'user'):
        await websocket.accept()
        connections_dict: dict = self._get_connection_dict_by_type(connection_type)
        connections_dict.setdefault(instance_id, set()).add(websocket)

    def disconnect(self, websocket: WebSocket, instance_id: int, connection_type: str = 'user'):
        connections_dict: dict = self._get_connection_dict_by_type(connection_type)
        connections_dict[instance_id].remove(websocket)

    async def send_message(self, message: TMessagePayload, instance_id: int, connection_type: str = 'user'):
        connections_dict: dict = self._get_connection_dict_by_type(connection_type)
        for websocket in connections_dict.get(instance_id, []):
            await websocket.send_text(message)


socket_service: SocketService = SocketService()
