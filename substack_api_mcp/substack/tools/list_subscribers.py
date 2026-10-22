"""List subscribers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.helpers import limit
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import next_cursor, offset_cursor, publication
from substack_api_mcp.substack.subscribers import plan_of, subscriber_page

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "plan": {
            "type": "string",
            "enum": ["all", "free", "paid", "comp", "founding"],
            "description": "all, free, paid, comp or founding. Default: all.",
        },
        "since": {
            "type": "string",
            "format": "date",
            "description": "Only subscribers who joined on or after this date.",
        },
        "limit": {"type": "integer", "description": "1 to 500. Default: 100."},
        "cursor": {"type": "string", "description": "Next page cursor from the previous call."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "subscribers": [
        {"email": "maya@example.com", "plan": "free", "joined_at": "2026-10-04T09:12:00Z", "activity_rating": 4},
        {"email": "jon@example.com", "plan": "paid", "joined_at": "2026-10-02T17:40:00Z", "activity_rating": 5},
    ],
    "next_cursor": None,
}


@tool(
    name="list_subscribers",
    title="List subscribers",
    access="read",
    confirm=False,
    description="Subscribers with plan, start date and activity rating.",
    details=(
        "Lists subscribers, newest first, from the subscriber dashboard. Activity rating is the 0 to 5 score "
        "Substack shows there. Pages hold up to 500 rows; pass next_cursor back as cursor. The plan and since "
        "filters apply inside each page, so a filtered page can be short or empty while next_cursor still "
        "points further. Someone added a minute ago may not show yet: Substack fills the table in the "
        "background. paid includes founding members."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /subscribers",
    example_response=EXAMPLE_RESPONSE,
)
async def list_subscribers(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    wanted = limit(args, 100, 500)
    offset = offset_cursor(args.get("cursor"))
    plan = args.get("plan") or "all"
    since = args.get("since")
    rows = await subscriber_page(ctx, pub, offset, wanted, since)
    subscribers = []
    for row in rows:
        row_plan = plan_of(row)
        if plan != "all" and row_plan != plan and not (plan == "paid" and row_plan == "founding"):
            continue
        subscribers.append(
            {
                "email": row.get("user_email_address"),
                "plan": row_plan,
                "joined_at": row.get("subscription_created_at"),
                "activity_rating": row.get("activity_rating"),
            }
        )
    return {"subscribers": subscribers, "next_cursor": next_cursor(offset, len(rows), wanted)}
