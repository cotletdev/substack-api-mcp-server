"""Get conversation."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, person

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "conversation_id": {"type": "string", "description": "Conversation ID from list_conversations."},
    },
    "required": ["conversation_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "conversation_id": "112992a4-5356-4bd2-8a16-f940cabbb4df",
    "members": [{"user_id": "41856304", "name": "Maya Chen", "handle": "mayachen"}],
    "messages": [
        {
            "from": {"user_id": "561078443", "name": "Sam Ortiz", "handle": "samortiz"},
            "body": "Hi, saw your Substack launch. Good luck with it!",
            "sent_at": "2026-10-18T15:55:22.545Z",
        }
    ],
}


@tool(
    name="get_conversation",
    title="Get conversation",
    access="read",
    confirm=False,
    description="The latest messages of one direct-message conversation, oldest first.",
    details=(
        "Returns who is in the conversation and its latest messages as the chat window first shows them, "
        "oldest first, with sender, text and time. Opening a conversation this way marks nothing read."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /conversations/{conversation_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_conversation(ctx: ToolContext, args: dict[str, Any]) -> Any:

    thread_id = str(args["conversation_id"]).strip().removeprefix("direct-message-")
    if not thread_id or "/" in thread_id:
        raise ToolError("conversation_id must be the ID from list_conversations.", ErrorCode.INVALID_INPUT)
    answer = await call(ctx, "GET", f"{WEB}/api/v1/messages/dm/{thread_id}")
    thread = answer.get("thread") or {}
    messages = [
        {
            "from": person(row.get("user") or {"id": (row.get("comment") or {}).get("user_id")}),
            "body": (row.get("comment") or {}).get("body") or "",
            "sent_at": (row.get("comment") or {}).get("created_at"),
        }
        for row in answer.get("replies") or []
        if row.get("comment")
    ]
    messages.sort(key=lambda message: message["sent_at"] or "")
    return {
        "conversation_id": thread.get("id") or thread_id,
        "members": [person(member.get("user")) for member in thread.get("members") or []],
        "messages": messages,
    }
