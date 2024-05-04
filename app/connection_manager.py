"""
This file contains the ConnectionManager class.

It is responsible for managing the WebSocket connections.
"""

import os
from asyncio import get_event_loop, sleep
from threading import Thread

from fastapi import WebSocket

HEARTBEAT_INTERVAL = int(os.getenv("HEARTBEAT_INTERVAL", "30"))
SHOW_PULSE_LEVEL = int(os.getenv("SHOW_PULSE", "1"))


class ConnectionManager:
    """Class that manages the WebSocket connections."""

    active_connections: dict[str, list[WebSocket]]
    hearbeat_thread: Thread

    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
        # self.hearbeat_thread = Thread(
        #     target=get_event_loop().run_until_complete, args=(self.heartbeat(),)
        # )
        # self.hearbeat_thread.start()

    async def heartbeat(self):
        """Sends a heartbeat message to all active connections every HEARTBEAT_INTERVAL seconds."""
        while True:
            await sleep(HEARTBEAT_INTERVAL)
            if SHOW_PULSE_LEVEL > 0:
                print("Pulse")
                if SHOW_PULSE_LEVEL > 1:
                    print("Active connections: ")
                    for group_name,connections in self.active_connections.items():
                        print(
                            f"{len(connections)} connections in group {group_name}"
                        )
            for group_name,connections in self.active_connections.items():
                for connection in connections:
                    await connection.send_text(
                        f"{len(connections)} connections in group {group_name}"
                    )

    async def connect(self, group_name: str, websocket: WebSocket):
        """Adds a new WebSocket connection to the list of active connections"""
        await websocket.accept()
        if group_name not in self.active_connections:
            self.active_connections[group_name] = []
        self.active_connections[group_name].append(websocket)

    def disconnect(self, group_name: str, websocket: WebSocket):
        """Removes a WebSocket connection from the list of active connections"""
        self.active_connections[group_name].remove(websocket)
        if not self.active_connections[group_name]:
            del self.active_connections[group_name]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        """Sends a message to a specific WebSocket connection"""
        await websocket.send_text(message)

    async def broadcast(self, group_name: str, message: str):
        """Sends a message to all active WebSocket connections in a group"""
        for connection in self.active_connections[group_name]:
            await connection.send_text(message)
