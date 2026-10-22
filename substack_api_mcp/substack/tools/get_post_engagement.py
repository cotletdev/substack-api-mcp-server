"""Get post engagement."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, person, post_id, publication

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
    "likes": 142,
    "liked_by": [{"user_id": "41856304", "name": "Maya Chen", "handle": "mayachen"}],
    "comments": 18,
    "commenters": 11,
    "commented_by": [{"user_id": "81309935", "name": "Sam Ortiz", "handle": "samortiz"}],
    "free_signups": 9,
    "paid_subscriptions": 1,
    "unsubscribes": 2,
}


@tool(
    name="get_post_engagement",
    title="Get post engagement",
    access="read",
    confirm=False,
    description="Who liked and commented on a post, and the subscribers it won and lost.",
    details=(
        "Returns the Engagement and Growth parts of a post's stats: like and comment counts with the people "
        "behind them (name and handle, never email), and the free signups, paid subscriptions and "
        "unsubscribes Substack credits to the post. Counts keep changing for days after a send."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /posts/{post_id}/engagement",
    example_response=EXAMPLE_RESPONSE,
)
async def get_post_engagement(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    base = f"{pub['base']}/api/v1/post_management/detail/{pid}"
    engagement = await call(ctx, "GET", f"{base}/engagement")
    growth = await call(ctx, "GET", f"{base}/growth")
    likes = engagement.get("likes") or {}
    commenters = engagement.get("commenters") or {}
    totals = (growth.get("subscribes") or {}).get("totals") or {}
    return {
        "post_id": str(pid),
        "likes": int(likes.get("count") or 0),
        "liked_by": [person(user) for user in likes.get("users") or []],
        "comments": int((engagement.get("commentSummary") or {}).get("total") or 0),
        "commenters": int(commenters.get("count") or 0),
        "commented_by": [person(user) for user in commenters.get("users") or []],
        "free_signups": int((growth.get("signups") or {}).get("total") or 0),
        "paid_subscriptions": int(totals.get("subscribes") or 0),
        "unsubscribes": int((growth.get("unsubscribes") or {}).get("total") or 0),
    }
