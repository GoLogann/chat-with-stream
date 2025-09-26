from __future__ import annotations
import uuid
from datetime import datetime, timezone
from typing import Optional, Dict, Any
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

from app.infra.dynamodb import DynamoClient


ISO = "%Y-%m-%dT%H:%M:%S.%fZ"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime(ISO)


class ChatRepository:
    def __init__(self, dynamo: DynamoClient):
        self.db = dynamo


    def create_chat(self, user_id: str, title: str) -> Dict[str, Any]:
        chat_id = str(uuid.uuid4())
        ts = now_iso()
        item = {
            "PK": f"USER#{user_id}",
            "SK": f"CHAT#{chat_id}",
            "type": "CHAT",
            "data": {
                "chat_id": chat_id,
                "user_id": user_id,
                "title": title,
                "created_at": ts,
                "updated_at": ts,
                "last_message_preview": None,
            },
            "GSI1PK": f"USER#{user_id}",
            "GSI1SK": f"CHAT#{ts}#{chat_id}",
        }
        self.db.put(item)
        return item["data"]

    def get_chat(self, user_id: str, chat_id: str) -> Optional[Dict[str, Any]]:
        item = self.db.get(pk=f"USER#{user_id}", sk=f"CHAT#{chat_id}")
        return item.get("data") if item else None

    def list_chats(self, user_id: str, limit: int = 20, last_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = {
            "IndexName": "GSI1",
            "KeyConditionExpression": Key("GSI1PK").eq(f"USER#{user_id}")
        }
        if limit:
            params["Limit"] = limit
        if last_key:
            params["ExclusiveStartKey"] = last_key
        res = self.db.query(**params)
        items = list(reversed(res.get("Items", [])))
        return {
            "items": [i["data"] for i in items],
            "last_evaluated_key": res.get("LastEvaluatedKey")
        }
    
    
    def update_chat_preview_and_ts(self, user_id: str, chat_id: str, preview: str):
        ts = now_iso()
        key = {"PK": f"USER#{user_id}", "SK": f"CHAT#{chat_id}"}
        update_expr = (
            "SET #data.#updated_at = :u, "
            "#data.#last_message_preview = :p, "
            "GSI1SK = :g1"
        )
        vals = {
            ":u": ts,
            ":p": preview,
            ":g1": f"CHAT#{ts}#{chat_id}"
        }
        names = {"#data": "data", "#updated_at": "updated_at", "#last_message_preview": "last_message_preview"}
        self.db.update(key, update_expr, vals, names)


    def append_message(self, chat_id: str, user_id: str, role: str, content: str, ttl: int = 0) -> Dict[str, Any]:
        msg_id = str(uuid.uuid4())
        ts = now_iso()
        item = {
            "PK": f"CHAT#{chat_id}",
            "SK": f"MSG#{ts}#{msg_id}",
            "type": "MSG",
            "data": {
                "message_id": msg_id,
                "chat_id": chat_id,
                "user_id": user_id,
                "role": role,
                "content": content,
                "created_at": ts,
            },
            "GSI4PK": f"USER#{user_id}#MSG",
            "GSI4SK": f"MSG#{ts}#{chat_id}#{msg_id}",
        }
        if ttl:
            item["ttl"] = ttl
        self.db.put(item)
        return item["data"]
    
    
    def get_messages(self, chat_id: str, limit: int = 100, last_key: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = {
            "KeyConditionExpression": Key("PK").eq(f"CHAT#{chat_id}") & Key("SK").begins_with("MSG#"),
            "ScanIndexForward": True,
        }
        if limit:
            params["Limit"] = limit
        if last_key:
            params["ExclusiveStartKey"] = last_key
        res = self.db.query(**params)
        return {
            "items": [i["data"] for i in res.get("Items", [])],
            "last_evaluated_key": res.get("LastEvaluatedKey")
        }
    
    
    def start_session(self, user_id: str, chat_id: str) -> Dict[str, Any]:
        session_id = str(uuid.uuid4())
        ts = now_iso()
        item = {
            "PK": f"USER#{user_id}",
            "SK": f"SESSION#{session_id}",
            "type": "SESSION",
            "data": {
                "session_id": session_id,
                "chat_id": chat_id,
                "user_id": user_id,
                "status": "active",
                "started_at": ts,
                "last_event_at": ts,
                "ended_at": None,
            },
            "GSI2PK": f"SESSION#STATUS#active",
            "GSI2SK": f"USER#{user_id}#START#{ts}#SESSION#{session_id}",
            "GSI3PK": f"CHAT#{chat_id}",
            "GSI3SK": f"SESSION#active#START#{ts}#SESSION#{session_id}",
        }
        self.db.put(item)
        return item["data"]
    
    
    def touch_session(self, user_id: str, session_id: str):
        ts = now_iso()
        key = {"PK": f"USER#{user_id}", "SK": f"SESSION#{session_id}"}
        update_expr = "SET #data.#last_event_at = :t"
        vals = {":t": ts}
        names = {"#data": "data", "#last_event_at": "last_event_at"}
        self.db.update(key, update_expr, vals, names)
    
    
    def end_session(self, user_id: str, session_id: str):
        ts = now_iso()
        key = {"PK": f"USER#{user_id}", "SK": f"SESSION#{session_id}"}
        update_expr = (
            "SET #data.#status = :e, "
            "#data.#ended_at = :t, "
            "GSI2PK = :p2, "
            "GSI3SK = :g3"
        )
        vals = {
            ":e": "ended",
            ":t": ts,
            ":p2": "SESSION#STATUS#ended",
            ":g3": f"SESSION#ended#START#{ts}#SESSION#{session_id}",
        }
        names = {"#data": "data", "#status": "status", "#ended_at": "ended_at"}
        try:
            self.db.update(key, update_expr, vals, names, condition="attribute_exists(PK)")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
                return
            raise