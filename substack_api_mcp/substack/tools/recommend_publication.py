"""Recommend publication."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "publication_id": {"type": "string", "description": "Publication ID, e.g. from search_substack posts."},
        "blurb": {"type": "string", "description": "Why you recommend it, shown to your readers (optional)."},
        "remove": {"type": "boolean", "description": "Stop recommending it instead. Default: false."},
    },
    "required": ["publication_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"publication_id": "5262902", "name": "Brain Health Decoded", "recommended": True}


@tool(
    name="recommend_publication",
    title="Recommend publication",
    access="write",
    confirm=True,
    description="Recommend another publication to your readers, or stop recommending it.",
    details=(
        "Adds a publication to your Recommendations, as Growth > Recommendations does: Substack suggests it "
        "to people who subscribe to you and notifies its author. blurb is the short reason readers see. With "
        "remove it takes the recommendation back. By default you confirm each call; you can switch that off "
        "for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /recommendations/{publication_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def recommend_publication(ctx: ToolContext, args: dict[str, Any]) -> Any:

    target = str(args["publication_id"]).strip()
    if not target.isdigit():
        raise ToolError("publication_id must be a numeric publication ID.", ErrorCode.INVALID_INPUT)
    pub = await publication(ctx)
    if int(target) == pub["id"]:
        raise ToolError("A publication cannot recommend itself.", ErrorCode.INVALID_INPUT)
    body: dict[str, Any] = {
        "recommended_publication_id": int(target),
        "recommending_publication_id": pub["id"],
        "source": "publisher_dashboard",
    }
    if args.get("remove"):
        await call(ctx, "DELETE", f"{pub['base']}/api/v1/recommendations", body=body)
        return {"publication_id": target, "name": None, "recommended": False}
    blurb = str(args.get("blurb") or "").strip()
    if blurb and len(blurb) < 2:
        raise ToolError("blurb must be at least 2 characters.", ErrorCode.INVALID_INPUT)
    body |= {"list_ids": [], "list_assignment": "add", **({"description": blurb} if blurb else {})}
    saved = await call(ctx, "PUT", f"{pub['base']}/api/v1/recommendations", body=body)
    name = (saved.get("recommendedPublication") or {}).get("name")
    return {"publication_id": target, "name": name, "recommended": True}
