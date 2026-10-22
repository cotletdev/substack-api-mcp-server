"""List subscriptions."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "subscriptions": [
        {
            "publication_id": "5262902",
            "name": "Brain Health Decoded",
            "url": "https://example.substack.com",
            "plan": "free",
            "emails": True,
            "since": "2026-10-18T13:46:36.900Z",
        }
    ]
}


@tool(
    name="list_subscriptions",
    title="List subscriptions",
    access="read",
    confirm=False,
    description="Publications you subscribe to, with your plan and whether their emails reach you.",
    details=(
        "Returns every publication your account subscribes to, as Settings > Subscriptions lists them: name, "
        "link, plan (free, paid, comp, founding or gift, as Substack names the membership) and whether you "
        "get its emails. Your own publications are left out."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /subscriptions",
    example_response=EXAMPLE_RESPONSE,
)
async def list_subscriptions(ctx: ToolContext, _args: dict[str, Any]) -> Any:

    answer = await call(ctx, "GET", f"{WEB}/api/v1/subscriptions/page_v2")
    pubs = {pub.get("id"): pub for pub in answer.get("publications") or []}
    own = {row.get("publication_id") for row in answer.get("publicationUsers") or []}
    subscriptions = []
    for row in answer.get("subscriptions") or []:
        pub = pubs.get(row.get("publication_id")) or {}
        if row.get("publication_id") in own:
            continue
        domain = pub.get("custom_domain") or (f"{pub['subdomain']}.substack.com" if pub.get("subdomain") else None)
        subscriptions.append(
            {
                "publication_id": str(row.get("publication_id") or ""),
                "name": pub.get("name") or "",
                "url": f"https://{domain}" if domain else None,
                "plan": _plan(row),
                "emails": not row.get("email_disabled"),
                "since": row.get("created_at"),
            }
        )
    return {"subscriptions": subscriptions}


def _plan(row: dict[str, Any]) -> str:
    if row.get("gift_user_id"):
        return "gift"
    if row.get("is_founding"):
        return "founding"
    state = str(row.get("membership_state") or "")
    if state == "free_signup":
        return "free"
    return "comp" if "comp" in state else "paid" if state else "free"
