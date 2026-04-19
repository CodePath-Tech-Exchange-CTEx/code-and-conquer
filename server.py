from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from google.cloud import bigquery
from datetime import datetime, timezone
import uuid
import json
import os

app = FastAPI()
client = bigquery.Client()

PROJECT_ID = os.getenv("GCP_PROJECT_ID", "daniel-reyes-uprm")
DATASET_ID = os.getenv("BQ_DATASET_ID", "iseGroupFour")
TABLE_ID = "Messages"
TABLE_REF = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"


class MessageIn(BaseModel):
    group_id: str
    sender_id: str
    content: str
    parent_message_id: str | None = None


class ConnectionManager:
    def __init__(self):
        self.rooms = {}

    async def connect(self, group_id: str, websocket: WebSocket):
        await websocket.accept()
        if group_id not in self.rooms:
            self.rooms[group_id] = []
        self.rooms[group_id].append(websocket)

    def disconnect(self, group_id: str, websocket: WebSocket):
        if group_id in self.rooms:
            self.rooms[group_id] = [ws for ws in self.rooms[group_id] if ws != websocket]
            if not self.rooms[group_id]:
                del self.rooms[group_id]

    async def broadcast(self, group_id: str, message: dict):
        if group_id in self.rooms:
            dead = []
            for ws in self.rooms[group_id]:
                try:
                    await ws.send_json(message)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                self.disconnect(group_id, ws)


manager = ConnectionManager()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/messages/{group_id}")
def get_messages(group_id: str):
    query = f"""
    SELECT id, group_id, sender_id, content, created_at, edited_at,
           is_deleted, parent_message_id
    FROM `{TABLE_REF}`
    WHERE group_id = @group_id
      AND is_deleted = FALSE
    ORDER BY created_at ASC
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("group_id", "STRING", group_id)
        ]
    )

    rows = client.query(query, job_config=job_config).result()

    messages = []
    for row in rows:
        messages.append({
            "id": row.id,
            "group_id": row.group_id,
            "sender_id": row.sender_id,
            "content": row.content,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "edited_at": row.edited_at.isoformat() if row.edited_at else None,
            "is_deleted": row.is_deleted,
            "parent_message_id": row.parent_message_id,
        })

    return {"messages": messages}


@app.post("/messages")
async def post_message(message: MessageIn):
    message_row = {
        "id": str(uuid.uuid4()),
        "group_id": message.group_id,
        "sender_id": message.sender_id,
        "content": message.content,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "edited_at": None,
        "is_deleted": False,
        "parent_message_id": message.parent_message_id,
    }

    errors = client.insert_rows_json(TABLE_REF, [message_row])

    if errors:
        return {"ok": False, "errors": errors}

    await manager.broadcast(message.group_id, message_row)
    return {"ok": True, "message": message_row}


@app.websocket("/ws/{group_id}")
async def websocket_chat(websocket: WebSocket, group_id: str):
    await manager.connect(group_id, websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)

            message_row = {
                "id": str(uuid.uuid4()),
                "group_id": group_id,
                "sender_id": data["sender_id"],
                "content": data["content"],
                "created_at": datetime.now(timezone.utc).isoformat(),
                "edited_at": None,
                "is_deleted": False,
                "parent_message_id": data.get("parent_message_id"),
            }

            errors = client.insert_rows_json(TABLE_REF, [message_row])

            if not errors:
                await manager.broadcast(group_id, message_row)
            else:
                await websocket.send_json({
                    "type": "error",
                    "errors": errors
                })

    except WebSocketDisconnect:
        manager.disconnect(group_id, websocket)