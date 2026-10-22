"""Get unread counts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

EXAMPLE_RESPONSE: dict[str, Any] = {"messages": 2, "message_requests": 1, "activity": 7}


@tool(
    name="get_unread_counts",
    title="Get unread counts",
    access="read",
    confirm=False,
    description="How many unread direct messages, message requests and activity notifications you have.",
    details=(
        "Returns the badges of the Substack app: unread direct messages, pending message requests and unread "
        "activity (likes, replies, new followers, restacks). Reading them marks nothing read."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /unread-counts",
    example_response=EXAMPLE_RESPONSE,
)
async def get_unread_counts(ctx: ToolContext, _args: dict[str, Any]) -> Any:

    messages = await call(ctx, "GET", f"{WEB}/api/v1/messages/unread-count")
    activity = await call(ctx, "GET", f"{WEB}/api/v1/activity/unread")
    return {
        "messages": int(messages.get("unreadCount") or 0),
        "message_requests": int(messages.get("pendingInviteCount") or 0),
        "activity": int(activity.get("count") or 0),
    }
