"""List traffic sources."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from substack_api_mcp.core.helpers import limit
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, next_cursor, offset_cursor, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "period": {"type": "string", "enum": ["7d", "30d", "90d", "365d"], "description": "Default: 30d."},
        "limit": {"type": "integer", "minimum": 1, "maximum": 50, "description": "Default: 20."},
        "cursor": {"type": "string", "description": "next_cursor from the previous page."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "period": "30d",
    "sources": [
        {
            "source": "substack app",
            "category": "Substack",
            "views": 8120,
            "visitors": 3011,
            "free_signups": 41,
            "paid_subscriptions": 3,
        }
    ],
    "next_cursor": None,
}


@tool(
    name="list_traffic_sources",
    title="List traffic sources",
    access="read",
    confirm=False,
    description="Where your publication's visitors came from in a period, most views first.",
    details=(
        "Returns Analytics > Traffic > Traffic sources: each source (the app, email, a website, search, "
        "social) with its category, views, unique visitors and the free and paid subscribers it brought. "
        "Sorted by views; page with next_cursor."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /traffic-sources",
    example_response=EXAMPLE_RESPONSE,
)
async def list_traffic_sources(ctx: ToolContext, args: dict[str, Any]) -> Any:

    period = args.get("period") or "30d"
    wanted = limit(args, 20, 50)  # Substack answers 400 above 50 (22.10.2026)
    offset = offset_cursor(args.get("cursor"))
    pub = await publication(ctx)
    today = datetime.now(ZoneInfo("Europe/Warsaw")).date()
    params = {
        "from_date": (today - timedelta(days=int(period[:-1]))).isoformat(),
        "to_date": today.isoformat(),
        "order_by": "views",
        "order_direction": "desc",
        "offset": offset,
        "limit": wanted,
    }
    answer = await call(ctx, "GET", f"{pub['base']}/api/v1/publication/stats/visitor_sources", params=params)
    rows = answer.get("rows") or []
    return {
        "period": period,
        "sources": [
            {
                "source": row.get("source") or "",
                "category": row.get("source_category") or "",
                "views": int(row.get("views") or 0),
                "visitors": int(row.get("users") or 0),
                "free_signups": int(row.get("free_signup") or 0),
                "paid_subscriptions": int(row.get("subscribed") or 0),
            }
            for row in rows
        ],
        "next_cursor": next_cursor(offset, len(rows), wanted),
    }
