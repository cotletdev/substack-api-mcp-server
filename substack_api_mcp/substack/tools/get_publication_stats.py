"""Get publication stats."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any
from zoneinfo import ZoneInfo

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "period": {"type": "string", "enum": ["7d", "30d", "90d"], "description": "7d, 30d or 90d. Default: 30d."}
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "period": "7d",
    "subscribers_total": 4380,
    "subscribers_paid": 412,
    "subscribers_new": 96,
    "subscribers_churned": 11,
    "revenue_usd": 725.48,
}


@tool(
    name="get_publication_stats",
    title="Get publication stats",
    access="read",
    confirm=False,
    description="Total and paid subscribers, new subscribers, paid cancellations and estimated revenue for a period.",
    details=(
        "Totals are from the publisher dashboard at the end of the period (7, 30 or 90 days). "
        "subscribers_churned counts paid cancellations only; Substack keeps no count of free unsubscribes. "
        "subscribers_new is the growth in total subscribers plus those cancellations. revenue_usd is not "
        "money received: it is the dashboard's annualized revenue at the end of the period, times the "
        "period's share of a year."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /stats",
    example_response=EXAMPLE_RESPONSE,
)
async def get_publication_stats(ctx: ToolContext, args: dict[str, Any]) -> Any:

    period = args.get("period") or "30d"
    days = int(period[:-1])
    pub = await publication(ctx)
    # The dashboard's summary for the last N days: subscribers and ARR at the start and the end.
    summary = await call(ctx, "GET", f"{pub['base']}/api/v1/publish-dashboard/summary-v2", params={"range": days})
    today = datetime.now(ZoneInfo("Europe/Warsaw")).date()
    window = {"from": (today - timedelta(days=days)).isoformat(), "to": today.isoformat(), "offset": 0, "limit": 1}
    # Cancelled paid subscriptions in the period (Analytics > Unsubscribes); Substack keeps no count of free ones.
    cancels = await call(ctx, "GET", f"{pub['base']}/api/v1/publication/stats/unsubscribes", params=window)
    churned = int(cancels.get("total") or 0)
    total_end = int(summary.get("totalSubscribersEnd") or 0)
    total_start = int(summary.get("totalSubscribersStart") or 0)
    # ARR is in cents, as Substack's other money fields; revenue is the period's share of it.
    arr = float(summary.get("arrEnd") or 0) / 100
    return {
        "period": period,
        "subscribers_total": total_end,
        "subscribers_paid": int(summary.get("paidSubscribersEnd") or 0),
        "subscribers_new": max(total_end - total_start + churned, 0),
        "subscribers_churned": churned,
        "revenue_usd": round(arr * days / 365, 2),
    }
