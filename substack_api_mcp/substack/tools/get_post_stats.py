"""Get post stats."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, post_id, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"post_id": {"type": "string", "description": "Post ID from list_posts."}},
    "required": ["post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "148213977",
    "recipients": 4120,
    "opens": 2011,
    "open_rate": 0.488,
    "views": 3560,
    "likes": 142,
    "restacks": 18,
    "subscribers_gained": 37,
}


@tool(
    name="get_post_stats",
    title="Get post stats",
    access="read",
    confirm=False,
    description="Recipients, opens, open rate, views, likes, restacks and subscribers gained.",
    details=(
        "Returns the engagement numbers of one published post, as on its stats page in the dashboard. Email "
        "numbers cover the send; views include the web; likes are reactions. A draft or scheduled post "
        "returns an error. Numbers keep growing for days after a send, so check again later."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /posts/{post_id}/stats",
    example_response=EXAMPLE_RESPONSE,
)
async def get_post_stats(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    detail = await call(
        ctx, "GET", f"{pub['base']}/api/v1/post_management/detail/{pid}", params={"offset": 0, "limit": 1}
    )
    rows = detail.get("posts") or []
    if not rows or not rows[0].get("is_published"):
        raise ToolError("This post is not published, so it has no stats yet.", ErrorCode.INVALID_INPUT)
    post = rows[0]
    stats = post.get("stats") or {}
    # Restacks are counted only on the public post.
    public = await call(ctx, "GET", f"{pub['base']}/api/v1/posts/{post['slug']}")
    sent = int(stats.get("sent") or 0)
    opened = int(stats.get("opened") or 0)
    return {
        "post_id": str(pid),
        "recipients": sent,
        "opens": opened,
        "open_rate": round(opened / sent, 3) if sent else 0.0,
        "views": int(stats.get("views") or 0),
        "likes": int(post.get("reaction_count") or 0),
        "restacks": int(public.get("restacks") or 0),
        "subscribers_gained": int(stats.get("signups") or 0),
    }
