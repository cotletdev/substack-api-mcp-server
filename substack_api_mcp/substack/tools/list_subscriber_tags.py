"""List subscriber tags."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

EXAMPLE_RESPONSE: dict[str, Any] = {"tags": [{"tag_id": "9357", "name": "Early readers"}]}


@tool(
    name="list_subscriber_tags",
    title="List subscriber tags",
    access="read",
    confirm=False,
    description="Tags you use to group subscribers.",
    details=(
        "Returns the subscriber tags of your publication with their IDs, as Audience > Subscribers > Tags "
        "shows them. Subscribers never see tags. Pass tag_id to tag_subscribers."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /subscriber-tags",
    example_response=EXAMPLE_RESPONSE,
)
async def list_subscriber_tags(ctx: ToolContext, _args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    answer = await call(ctx, "GET", f"{pub['base']}/api/v1/subscriber-tags")
    return {"tags": [{"tag_id": str(row["id"]), "name": row.get("name") or ""} for row in answer.get("tags") or []]}
