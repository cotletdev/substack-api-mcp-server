"""List posts."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.helpers import limit
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import (
    call,
    next_cursor,
    offset_cursor,
    post_status,
    post_url,
    publication,
    scheduled_at,
)

# Status -> dashboard list and its order, as the Posts tabs of the dashboard ask for them.
_LISTS = {
    "published": ("published", "post_date", "desc"),
    "draft": ("drafts", "draft_updated_at", "desc"),
    "scheduled": ("scheduled", "trigger_at", "asc"),
}

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "status": {
            "type": "string",
            "enum": ["published", "draft", "scheduled"],
            "description": "published, draft or scheduled. Default: published.",
        },
        "limit": {"type": "integer", "description": "1 to 50. Default: 20."},
        "cursor": {"type": "string", "description": "Next page cursor from the previous call."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "posts": [
        {
            "post_id": "148213977",
            "title": "The quiet launch",
            "status": "published",
            "audience": "everyone",
            "published_at": "2026-10-06T12:00:00Z",
            "url": "https://yourname.substack.com/p/the-quiet-launch",
        },
        {
            "post_id": "148420031",
            "title": "Notes on pricing",
            "status": "draft",
            "audience": "only_paid",
            "published_at": None,
            "url": None,
        },
    ],
    "next_cursor": "eyJvZmZzZXQiOjIwfQ",
}


@tool(
    name="list_posts",
    title="List posts",
    access="read",
    confirm=False,
    description="Posts of your publication, newest first, with status and audience.",
    details=(
        "Lists posts of your publication, newest first. Filter by status to see drafts or scheduled posts. "
        "Scheduled posts include their publish time. Pages hold up to 50 posts; pass next_cursor back as "
        "cursor for the next page."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /posts",
    example_response=EXAMPLE_RESPONSE,
)
async def list_posts(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    status = args.get("status") or "published"
    endpoint, order_by, direction = _LISTS[status]
    wanted = limit(args, 20, 50)
    offset = offset_cursor(args.get("cursor"))
    params = {"offset": offset, "limit": wanted, "order_by": order_by, "order_direction": direction}
    answer = await call(ctx, "GET", f"{pub['base']}/api/v1/post_management/{endpoint}", params=params)
    rows = answer.get("posts") or []
    posts = []
    for post in rows:
        item = {
            "post_id": str(post["id"]),
            "title": post.get("title") or post.get("draft_title") or "",
            "status": post_status(post),
            "audience": post.get("audience"),
            "published_at": post.get("post_date") if post.get("is_published") else None,
            "url": post_url(pub, post),
        }
        if item["status"] == "scheduled":
            item["publish_at"] = scheduled_at(post)
        posts.append(item)
    return {"posts": posts, "next_cursor": next_cursor(offset, len(rows), wanted)}
