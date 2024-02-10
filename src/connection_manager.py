import json
from dataclasses import dataclass
import uuid
from fastapi import WebSocket

from src.user import User


@dataclass
class ConnectionManager:
    def __init__(self) -> None:
        self.connections: dict = {}

    async def connect(self, websocket: WebSocket):
        # Wait until connection is stablished
        await websocket.accept()

        id = str(uuid.uuid4())
        self.connections[id] = websocket

        await self.send_message(websocket, json.dumps({"type": "New Connection", "Username": id}))

    def disconnect(self, websocket: WebSocket):
        id = self.find_connection_id(websocket)
        del self.connections[id]
        return id

    def find_connection_id(self, websocket: WebSocket):
        val_list = list(self.connections.values())
        key_list = list(self.connections.keys())
        id = val_list.index(websocket)
        return key_list[id]

    async def send_message(self, websocket: WebSocket, message: str):
        await websocket.send_text(message)

    async def broadcast(self, websocket: WebSocket, message: str):
        for connection in self.connections:
            if self.connections[connection] != websocket:
                await self.connections[connection].send_text(message)
