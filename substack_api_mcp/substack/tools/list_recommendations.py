"""List recommendations."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "direction": {
            "type": "string",
            "enum": ["given", "received"],
            "description": "given (publications you recommend) or received (that recommend you). Default: given.",
        },
        "publication_id": {
            "type": "string",
            "description": "Check one publication instead: does yours recommend it (given only).",
        },
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "direction": "given",
    "recommendations": [
        {
            "publication_id": "5262902",
            "name": "Brain Health Decoded",
            "blurb": "The best science newsletter I read.",
            "active": True,
            "mutual": None,
            "since": "2026-10-18T16:35:11.246Z",
            "subscribers_sent": 12,
        }
    ],
    "counts": {"given": 1, "received": 0, "subscribers_from_recommendations": 0},
}


@tool(
    name="list_recommendations",
    title="List recommendations",
    access="read",
    confirm=False,
    description="Publications you recommend, or that recommend you, with the subscribers each sent.",
    details=(
        "Returns Audience > Recommendations: with direction given, the publications you recommend; with "
        "received, the ones recommending you, and whether you recommend them back (mutual). "
        "subscribers_sent counts subscribers the recommendation brought. The table is rebuilt by Substack "
        "in the background, so a recommendation made minutes ago may be missing while counts already "
        "include it; publication_id checks one recommendation of yours directly."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /recommendations",
    example_response=EXAMPLE_RESPONSE,
)
async def list_recommendations(ctx: ToolContext, args: dict[str, Any]) -> Any:

    direction = args.get("direction") or "given"
    pub = await publication(ctx)
    base = f"{pub['base']}/api/v1/recommendations"
    exist = await call(ctx, "GET", f"{base}/exist")
    if args.get("publication_id"):
        target = str(args["publication_id"]).strip()
        found = await call(ctx, "GET", f"{base}/from/{pub['id']}/to/{target}") if target.isdigit() else {}
        target_pub = (found or {}).get("recommendedPublication") or {}
        rows = [{**found, "target_pub": {**target_pub, "id": target}, "is_active": True}] if found else []
        direction = "given"
    else:
        rows = await _all(ctx, f"{base}/stats/{'from' if direction == 'given' else 'to'}")
    side = "target_pub" if direction == "given" else "source_pub"
    return {
        "direction": direction,
        "recommendations": [
            {
                "publication_id": str((row.get(side) or {}).get("id") or ""),
                "name": (row.get(side) or {}).get("name") or "",
                "blurb": row.get("description") or row.get("blurb"),
                "active": bool(row.get("is_active")),
                "mutual": row.get("is_mutual") if direction == "received" else None,
                "since": row.get("created_at"),
                "subscribers_sent": int(row.get("xp_signups") or 0),
            }
            for row in rows
        ],
        "counts": {
            "given": int(exist.get("recommendingOthers") or 0),
            "received": int(exist.get("beingRecommended") or 0),
            "subscribers_from_recommendations": int(exist.get("totalSignups") or 0),
        },
    }


async def _all(ctx: ToolContext, url: str) -> list[dict[str, Any]]:
    """The dashboard reads the table 20 rows at a time until it has them all."""
    rows: list[dict[str, Any]] = []
    for offset in range(0, 1000, 20):
        page = await call(ctx, "GET", url, params={"offset": offset, "limit": 20})
        rows += page.get("rows") or []
        if offset + 20 >= int(page.get("total") or 0):
            break
    return rows
