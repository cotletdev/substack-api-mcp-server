"""Get audience insights."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "region": {
            "type": "string",
            "enum": ["world", "usa"],
            "description": "world (by country) or usa (by state). Default: world.",
        },
        "paid_only": {"type": "boolean", "description": "Count paid subscribers only. Default: false."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "region": "world",
    "metric": "all subscribers",
    "countries_total": 41,
    "us_states_total": 38,
    "locations": [{"location": "us", "subscribers": 2310}, {"location": "gb", "subscribers": 402}],
    "overlap": [
        {
            "publication_id": "5262902",
            "name": "Brain Health Decoded",
            "url": "https://example.substack.com",
            "overlap_percent": 6.4,
        }
    ],
}


@tool(
    name="get_audience_insights",
    title="Get audience insights",
    access="read",
    confirm=False,
    description="Where your subscribers live, and which publications share your readers.",
    details=(
        "Returns Analytics > Statistics > Audience: subscriber counts per country (region world, ISO codes "
        "such as us, gb) or per US state (region usa, codes such as ny, ca), all subscribers or paid only, "
        "the number of countries and states with any subscriber, and the publications whose readers "
        "overlap most with yours. Substack computes these in the background; a new publication has empty "
        "lists for a while."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /audience",
    example_response=EXAMPLE_RESPONSE,
)
async def get_audience_insights(ctx: ToolContext, args: dict[str, Any]) -> Any:

    region = args.get("region") or "world"
    metric = "paid subscribers" if args.get("paid_only") else "free signups"
    pub = await publication(ctx)
    stats = f"{pub['base']}/api/v1/publication/stats/audience_insights"
    params = {"metric": metric, "granularity": "usa" if region == "usa" else "global"}
    rows = await call(ctx, "GET", f"{stats}/location", params=params) or []
    totals = await call(ctx, "GET", f"{stats}/location/total") or {}
    overlap = await call(ctx, "GET", f"{stats}/overlap", params={"limit": 10}) or []
    locations = sorted(
        (
            {"location": str(row.get("location") or "").lower(), "subscribers": int(row.get("value") or 0)}
            for row in rows
        ),
        key=lambda row: -row["subscribers"],
    )
    return {
        "region": region,
        "metric": "paid subscribers" if args.get("paid_only") else "all subscribers",
        "countries_total": int((totals.get("global") or {}).get("locations") or 0),
        "us_states_total": int((totals.get("usa") or {}).get("locations") or 0),
        "locations": locations,
        "overlap": [
            {
                "publication_id": str((row.get("pub") or {}).get("id") or ""),
                "name": (row.get("pub") or {}).get("name") or "",
                "url": (row.get("pub") or {}).get("base_url"),
                "overlap_percent": row.get("percentOverlap"),
            }
            for row in overlap
        ],
    }
