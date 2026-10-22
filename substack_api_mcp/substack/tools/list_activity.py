"""List activity."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, person

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

_FILTERS = {"all": "all", "replies": "replies-and-mentions", "restacks": "restacks"}

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "filter": {
            "type": "string",
            "enum": ["all", "replies", "restacks"],
            "description": "all, replies (replies and mentions) or restacks. Default: all.",
        },
        "cursor": {"type": "string", "description": "next_cursor from the previous page."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "activity": [
        {
            "type": "note_reply",
            "at": "2026-10-18T16:35:45.367Z",
            "from": [{"user_id": "561099060", "name": "Maya Chen", "handle": "mayachen"}],
            "people": 1,
            "comment_id": "364181517",
            "text": "Rain walks are underrated. Boots or sneakers?",
            "on_comment_id": "364181148",
            "on_post_id": None,
        },
        {
            "type": "follow",
            "at": "2026-10-18T16:34:31.102Z",
            "from": [{"user_id": "561099060", "name": "Maya Chen", "handle": "mayachen"}],
            "people": 1,
            "comment_id": None,
            "text": None,
            "on_comment_id": None,
            "on_post_id": None,
        },
    ],
    "next_cursor": None,
}


@tool(
    name="list_activity",
    title="List activity",
    access="read",
    confirm=False,
    description="Your Substack notifications: replies, likes, new followers, restacks, newest first.",
    details=(
        "Returns the Activity tab of the Substack app, newest first. type is Substack's own name, e.g. "
        "note_reply, note_like, comment_reply, comment_like, post_like, follow, restack or mention. from lists "
        "the latest people behind a grouped item and people counts all of them. A reply or mention carries "
        "its comment_id and text; on_comment_id and on_post_id point at what it was about. Reading the list "
        "marks nothing read. Page with next_cursor."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /activity",
    example_response=EXAMPLE_RESPONSE,
)
async def list_activity(ctx: ToolContext, args: dict[str, Any]) -> Any:

    params: dict[str, Any] = {"filter": _FILTERS[args.get("filter") or "all"]}
    if args.get("cursor"):
        params["after"] = args["cursor"]
    answer = await call(ctx, "GET", f"{WEB}/api/v1/activity-feed-web", params=params)
    users = {user.get("id"): user for user in answer.get("users") or []}
    texts = {
        c.get("id"): c.get("body") for c in (answer.get("comments") or []) + (answer.get("feedItemComments") or [])
    }
    items = answer.get("activityItems") or []
    activity = [
        {
            "type": item.get("type") or "",
            "at": item.get("updated_at") or item.get("created_at"),
            "from": [person(users[uid]) for uid in item.get("recent_sender_ids") or [] if uid in users],
            "people": int(item.get("sender_count") or 0),
            "comment_id": _id(item.get("comment_id")),
            "text": texts.get(item.get("comment_id")) if item.get("comment_id") else None,
            "on_comment_id": _id(item.get("target_comment_id")),
            "on_post_id": _id(item.get("target_post_id")),
        }
        for item in items
    ]
    return {"activity": activity, "next_cursor": _cursor(items) if answer.get("more") else None}


def _id(value: Any) -> str | None:
    return str(value) if value else None


def _cursor(items: list[dict[str, Any]]) -> str | None:
    """The app pages back from the oldest item's time, one millisecond earlier."""
    stamps = [item["updated_at"] for item in items if item.get("updated_at")]
    if not stamps:
        return None
    oldest = min(datetime.fromisoformat(stamp.replace("Z", "+00:00")) for stamp in stamps)
    return (oldest - timedelta(milliseconds=1)).isoformat(timespec="milliseconds").replace("+00:00", "Z")
