"""
This is the main file for the FastAPI application. It contains the main application logic and routes.
"""

import json
import pathlib

from fastapi import Depends, FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session

from app.db_controller import (
    get_destiny_state,
    get_history,
    get_character_states,
)
from app.dependencies import get_session, manager, message_bus, templates
from app.models import create_db_and_tables

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
create_db_and_tables()


@app.get("/main/{group_name}/")
async def get_group_state(
    request: Request,
    group_name: str,
    char_name: str,
    session: Session = Depends(get_session),
):
    # get current state
    destiny_states = get_destiny_state(group_name, session)

    # get history
    history = get_history(group_name, session)
    messages = sorted([
        message_bus.message_types[history_event.event_type].from_json(history_event.json_data)
        for history_event in history
    ], key=lambda x: x.created_at)

    # get character states
    character_states = get_character_states(group_name, session)

    return templates.TemplateResponse(
        "mainpage.html",
        {
            "request": request,
            "destiny_states": destiny_states,
            "messages": messages,
            "char_name": char_name,
            "group_name": group_name,
            "character_states": character_states,
        },
    )



@app.websocket("/ws/{group_name}/{client_name}")
async def websocket_endpoint(websocket: WebSocket, group_name: str, client_name: str):
    await manager.connect(group_name, websocket)
    while True:
        try:
            data = await websocket.receive_text()
            print("received:", data)
            if data.startswith("Hello"):
                await manager.send_personal_message(
                    f"Hello Client #{client_name}", websocket
                )
                continue

            data = json.loads(data)
            # ensure author and group_name are set
            data["author"] = client_name
            data["group_name"] = group_name
            await message_bus.process_message(data)
        except ValueError as e:
            print("ERROR", e)
        except WebSocketDisconnect:
            manager.disconnect(group_name, websocket)
            await manager.broadcast(group_name, f"Client #{client_name} left the chat")
