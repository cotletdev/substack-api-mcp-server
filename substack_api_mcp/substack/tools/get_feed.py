"""Get feed."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call
from substack_api_mcp.substack.feed import note_item, post_item

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "tab": {
            "type": "string",
            "enum": ["for_you", "following"],
            "description": "for_you (Substack's picks) or following (whom you follow). Default: for_you.",
        },
        "cursor": {"type": "string", "description": "next_cursor from the previous page."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "tab": "following",
    "posts": [
        {
            "post_id": "197396217",
            "title": "A Guide to Your Morning Routine",
            "publication": "Brain Health Decoded",
            "publication_id": "5262902",
            "published_at": "2026-05-12T19:25:47.700Z",
            "likes": 410,
            "url": "https://example.substack.com/p/a-guide-to-your-morning-routine",
        }
    ],
    "notes": [
        {
            "note_id": "322981144",
            "author": {"user_id": "18270011", "name": "Laura Mills", "handle": "lauramills"},
            "body": "Morning light beats any supplement.",
            "published_at": "2026-09-02T07:11:00.000Z",
            "likes": 88,
        }
    ],
    "next_cursor": "eyJzZXNzaW9uX2lkIjoiZWQzOCJ9",
}


@tool(
    name="get_feed",
    title="Get feed",
    access="read",
    confirm=False,
    description="Your Substack home feed: posts and Notes, For you or Following.",
    details=(
        "Returns one page of the home feed of the Substack app, split into posts and Notes in feed order. "
        "for_you is Substack's own mix; following holds only people and publications you follow or "
        "subscribe to. Suggestions of people to follow are left out. Reading marks nothing seen. Page with "
        "next_cursor; the feed is personal and changes between calls."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /feed",
    example_response=EXAMPLE_RESPONSE,
)
async def get_feed(ctx: ToolContext, args: dict[str, Any]) -> Any:

    tab = args.get("tab") or "for_you"
    params = {"tab": "subscribed" if tab == "following" else "for-you", "type": "base"}
    if args.get("cursor"):
        params["cursor"] = args["cursor"]
    answer = await call(ctx, "GET", f"{WEB}/api/v1/reader/feed", params=params)
    items = answer.get("items") or []
    return {
        "tab": tab,
        "posts": [post_item(item) for item in items if item.get("type") == "post" and item.get("post")],
        "notes": [note_item(item) for item in items if item.get("type") == "comment" and item.get("comment")],
        "next_cursor": answer.get("nextCursor"),
    }
