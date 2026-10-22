"""The dashboard's subscriber table (Audience > Subscribers) and its CSV export.

The table is `POST /api/v1/subscriber-stats` with the dashboard's filters. Substack fills it from its own
index in the background, so a subscriber added a minute ago may not be listed yet.
The export builds a subscriber set from the same order, asks for a CSV of it and polls until Substack
hands out the file, as the dashboard's Export button does (`exportSubscriberSet` in its bundle, 17.10.2026).
"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any
from urllib.parse import parse_qs, urlsplit

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.substack.client import call

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

_ORDER = {"order_by_desc_nulls_last": "subscription_created_at"}
_COLUMNS = ["user_email_address", "user_name", "subscription_type", "activity_rating", "subscription_created_at"]
# Seconds between polls for the export file, as the dashboard waits: 1, 5, 10, then 30.
_POLL_S = (1, 4, 5, 10, 10, 15)


def plan_of(row: dict[str, Any]) -> str:
    """free, paid, comp or founding, as the subscriber table labels the row."""
    if row.get("is_comp"):
        return "comp"
    if row.get("is_founding"):
        return "founding"
    kind = str(row.get("subscription_type") or "").lower()
    return "free" if not kind or "free" in kind else "paid"


async def subscriber_page(
    ctx: ToolContext, pub: dict[str, Any], offset: int, size: int, since: str | None
) -> list[dict[str, Any]]:
    """One page of the table, newest first; `since` stops at subscribers who joined before that date."""
    body = {"filters": _ORDER, "limit": size, "offset": offset, "includeTags": False}
    answer = await call(ctx, "POST", f"{pub['base']}/api/v1/subscriber-stats", body=body)
    rows = answer.get("subscribers") or []
    if since:
        rows = [row for row in rows if (row.get("subscription_created_at") or "")[:10] >= since[:10]]
    return rows


async def export(ctx: ToolContext, pub: dict[str, Any]) -> dict[str, Any]:
    base = f"{pub['base']}/api/v1"
    subscriber_set = await call(ctx, "POST", f"{base}/subscriber_set", body={"query": _ORDER})
    if not subscriber_set.get("id"):
        raise ToolError("Substack did not start the export.", ErrorCode.TARGET_ERROR)
    body = {"subscriberSetId": subscriber_set["id"], "columns": _COLUMNS}
    job = await call(ctx, "POST", f"{base}/subscriber_set/export", body=body)
    for wait_s in _POLL_S:
        await asyncio.sleep(wait_s)
        response = await ctx.call("GET", f"{base}/subscriber_set/export/{job.get('export_id')}")
        path = response.json().get("url") if response.status == 200 else None
        if path:
            return await _file(ctx, pub, path)
    raise ToolError("Substack is still building the export; try again in a few minutes.", ErrorCode.TIMEOUT)


async def _file(ctx: ToolContext, pub: dict[str, Any], path: str) -> dict[str, Any]:
    """The export's `/file` path redirects to a presigned S3 link: that link is the answer, valid without cookies."""
    response = await call_file(ctx, f"{pub['base']}{path}")
    query = parse_qs(urlsplit(response.url).query)
    signed = datetime.strptime(query["X-Amz-Date"][0], "%Y%m%dT%H%M%SZ").replace(tzinfo=UTC)
    lines = [line for line in response.text.splitlines() if line.strip()]
    return {
        "download_url": response.url,
        "rows": max(len(lines) - 1, 0),
        "expires_at": (signed + timedelta(seconds=int(query["X-Amz-Expires"][0]))).isoformat(),
    }


async def call_file(ctx: ToolContext, url: str) -> Any:
    response = await ctx.call("GET", url, headers={"accept": "text/csv"})
    if response.status != 200 or "X-Amz-Expires" not in response.url:
        raise ToolError("Substack did not hand out the export file.", ErrorCode.TARGET_ERROR)
    return response


async def find_subscriber(ctx: ToolContext, pub: dict[str, Any], email: str) -> dict[str, Any] | None:
    """The table row of one email: the dashboard's search box, then an exact match on the address."""
    body = {"filters": {**_ORDER, "search": email}, "limit": 10, "offset": 0, "includeTags": False}
    answer = await call(ctx, "POST", f"{pub['base']}/api/v1/subscriber-stats", body=body)
    wanted = email.strip().lower()
    return next(
        (row for row in answer.get("subscribers") or [] if str(row.get("user_email_address")).lower() == wanted),
        None,
    )
