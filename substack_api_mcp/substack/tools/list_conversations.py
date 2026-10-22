"""List conversations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "unread_only": {"type": "boolean", "description": "Only conversations with unread messages."},
        "cursor": {"type": "string", "description": "next_cursor from the previous page."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "conversations": [
        {
            "conversation_id": "112992a4-5356-4bd2-8a16-f940cabbb4df",
            "with": "Maya Chen",
            "last_message": "Also, what newsletter tool did you switch from?",
            "last_from_you": True,
            "last_at": "2026-10-18T15:55:35.587Z",
            "unread": 0,
            "is_request": False,
        }
    ],
    "next_cursor": None,
}


@tool(
    name="list_conversations",
    title="List conversations",
    access="read",
    confirm=False,
    description="Your direct-message conversations, latest first, with the last message.",
    details=(
        "Returns your Substack chat inbox: one-to-one and group direct messages with who they are with, the "
        "last message, its time, your unread count and whether it is a message request from someone you do "
        "not follow. Publication chats are left out. Reading the list does not mark anything read. Pass "
        "conversation_id to get_conversation or send_message."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /conversations",
    example_response=EXAMPLE_RESPONSE,
)
async def list_conversations(ctx: ToolContext, args: dict[str, Any]) -> Any:

    params = {"tab": "unread" if args.get("unread_only") else "all"}
    if args.get("cursor"):
        params["cursor"] = args["cursor"]
    answer = await call(ctx, "GET", f"{WEB}/api/v1/messages/inbox", params=params)
    conversations = []
    for row in answer.get("threads") or []:
        thread = row.get("messageThread") or {}
        if row.get("type") != "direct-message" or not thread.get("id"):
            continue
        recent = row.get("recentMessage") or {}
        conversations.append(
            {
                "conversation_id": thread["id"],
                "with": row.get("title") or thread.get("name") or "",
                "last_message": recent.get("body") or row.get("subtitleBody") or "",
                "last_from_you": row.get("subtitleName") == "You",
                "last_at": row.get("timestamp") or recent.get("created_at"),
                "unread": int(row.get("unreadCount") or 0),
                "is_request": bool(row.get("isRequest")),
            }
        )
    return {"conversations": conversations, "next_cursor": answer.get("nextCursor")}
