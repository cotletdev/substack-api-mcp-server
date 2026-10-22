"""Send message."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, user_ref

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "conversation_id": {"type": "string", "description": "Reply in this conversation from list_conversations."},
        "user": {"type": "string", "description": "Or start one with this handle (e.g. @mayachen) or user ID."},
        "body": {"type": "string", "description": "Message text."},
    },
    "required": ["body"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "conversation_id": "112992a4-5356-4bd2-8a16-f940cabbb4df",
    "sent_at": "2026-10-18T15:55:35.587Z",
}


@tool(
    name="send_message",
    title="Send message",
    access="write",
    confirm=True,
    description="Send a direct message on Substack, in a conversation or to a person.",
    details=(
        "Sends a private chat message under your name. With conversation_id it replies there; with user it "
        "writes to that person, in your existing conversation with them or a new one. Someone who does not "
        "follow you gets it as a message request. Give one of conversation_id or user. A sent message cannot "
        "be recalled. By default you confirm each call; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /messages",
    example_response=EXAMPLE_RESPONSE,
)
async def send_message(ctx: ToolContext, args: dict[str, Any]) -> Any:

    text = str(args["body"]).strip()
    if not text:
        raise ToolError("body must not be empty.", ErrorCode.INVALID_INPUT)
    if bool(args.get("conversation_id")) == bool(args.get("user")):
        raise ToolError("Give one of conversation_id or user.", ErrorCode.INVALID_INPUT)
    if args.get("conversation_id"):
        thread_id = str(args["conversation_id"]).strip().removeprefix("direct-message-")
        if "/" in thread_id:
            raise ToolError("conversation_id must be the ID from list_conversations.", ErrorCode.INVALID_INPUT)
        answer = await call(ctx, "POST", f"{WEB}/api/v1/messages/dm/{thread_id}", body={"body": text})
    else:
        user = await user_ref(ctx, args["user"])
        answer = await call(ctx, "POST", f"{WEB}/api/v1/messages/dm", body={"user_id": user["id"], "body": text})
    thread = answer.get("thread") or {}
    reply = answer.get("reply") or {}
    sent = (reply.get("comment") or reply).get("created_at")
    return {"conversation_id": thread.get("id"), "sent_at": sent or thread.get("updated_at")}
