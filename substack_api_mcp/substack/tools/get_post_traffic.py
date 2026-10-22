"""Get post traffic."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

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
    "sources": [{"source": "substack app", "views": 812, "share": 0.41, "free_signups": 12, "paid_subscriptions": 2}],
    "categories": [{"category": "Substack", "share": 0.58}],
    "devices": [{"device": "mobile", "share": 0.66}],
}


@tool(
    name="get_post_traffic",
    title="Get post traffic",
    access="read",
    confirm=False,
    description="Where a post's readers came from: sources, categories and devices.",
    details=(
        "Returns the Traffic part of a post's stats: each source (app, email, a website, search) with its "
        "views, share of all views and the free and paid subscribers it brought, the share per source "
        "category and per device. A post nobody has read yet returns empty lists."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /posts/{post_id}/traffic",
    example_response=EXAMPLE_RESPONSE,
)
async def get_post_traffic(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    answer = await call(ctx, "GET", f"{pub['base']}/api/v1/post_management/detail/{pid}/traffic")
    return {
        "post_id": str(pid),
        "sources": [
            {
                "source": row.get("source") or row.get("name") or "",
                "views": int(row.get("views") or 0),
                "share": _share(row),
                "free_signups": int(row.get("signups") or 0),
                "paid_subscriptions": int(row.get("subscribes") or 0),
            }
            for row in answer.get("referrers") or []
        ],
        "categories": [
            {"category": row.get("category_type") or row.get("name") or "", "share": _share(row)}
            for row in answer.get("categories") or []
        ],
        "devices": [
            {"device": row.get("device_type") or row.get("name") or "", "share": _share(row)}
            for row in answer.get("devices") or []
        ],
    }


def _share(row: dict[str, Any]) -> float:
    return round(float(row.get("percent_of_total_views") or 0), 3)
