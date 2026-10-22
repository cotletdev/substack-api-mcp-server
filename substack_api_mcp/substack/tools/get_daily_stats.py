"""Get daily stats."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"period": {"type": "string", "enum": ["7d", "30d", "90d", "365d"], "description": "Default: 30d."}},
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "period": "7d",
    "days": [{"date": "2026-10-18", "subscribers": 4380, "paid_subscribers": 412, "followers": 5120, "views": 1893}],
}


@tool(
    name="get_daily_stats",
    title="Get daily stats",
    access="read",
    confirm=False,
    description="Day by day: total and paid subscribers, followers and views.",
    details=(
        "Returns one row per day of the period, as the charts on the dashboard home and in Audience: total "
        "subscribers, paid subscribers and followers at the end of the day, and the day's views across your "
        "site and the app. Days Substack has no number for are null; a young publication starts on the day "
        "it was made."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /stats/daily",
    example_response=EXAMPLE_RESPONSE,
)
async def get_daily_stats(ctx: ToolContext, args: dict[str, Any]) -> Any:

    period = args.get("period") or "30d"
    pub = await publication(ctx)
    since = (datetime.now(UTC) - timedelta(days=int(period[:-1]))).strftime("%Y-%m-%dT%H:%M:%S.000Z")
    stats = f"{pub['base']}/api/v1/publication/stats"
    columns = {
        "subscribers": await _series(ctx, f"{stats}/emails/timeseries", since),
        "paid_subscribers": await _series(ctx, f"{stats}/subscribers/timeseries", since, "Paid"),
        "followers": await _series(ctx, f"{stats}/followers/timeseries", since),
        "views": await _series(ctx, f"{stats}/publication_traffic/timeseries", since, resolution="day"),
    }
    dates = sorted({date for series in columns.values() for date in series})
    return {
        "period": period,
        "days": [{"date": date, **{name: series.get(date) for name, series in columns.items()}} for date in dates],
    }


async def _series(
    ctx: ToolContext, url: str, since: str, column: str | None = None, resolution: str | None = None
) -> dict[str, int | None]:
    """A dashboard chart as {date: value}. Rows are [date, value]; with a header row, `column` picks the value."""
    params = {"from": since, **({"resolution": resolution} if resolution else {})}
    rows = await call(ctx, "GET", url, params=params) or []
    index = 1
    if rows and isinstance(rows[0], list) and rows[0] and rows[0][0] == "Date":
        index = rows[0].index(column) if column in rows[0] else 1
        rows = rows[1:]
    series: dict[str, int | None] = {}
    for row in rows:
        if isinstance(row, list) and len(row) > index:
            value = row[index]
            series[str(row[0]).replace("/", "-")] = int(value) if isinstance(value, int | float) else None
    return series
