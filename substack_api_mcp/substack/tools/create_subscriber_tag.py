"""Create subscriber tag."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"name": {"type": "string", "description": "Tag name, e.g. Early readers."}},
    "required": ["name"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"tag_id": "9357", "name": "Early readers"}


@tool(
    name="create_subscriber_tag",
    title="Create subscriber tag",
    access="write",
    confirm=False,
    description="New private tag for grouping subscribers.",
    details=(
        "Creates a subscriber tag on your publication. Tags are private: subscribers never see them. Put "
        "subscribers under it with tag_subscribers."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /subscriber-tags",
    example_response=EXAMPLE_RESPONSE,
)
async def create_subscriber_tag(ctx: ToolContext, args: dict[str, Any]) -> Any:

    name = str(args["name"]).strip()
    if not name or len(name) > 100:
        raise ToolError("name must be 1 to 100 characters.", ErrorCode.INVALID_INPUT)
    pub = await publication(ctx)
    answer = await call(ctx, "POST", f"{pub['base']}/api/v1/subscriber-tags", body={"name": name})
    tag = answer.get("tag") or answer
    return {"tag_id": str(tag["id"]), "name": tag.get("name") or name}
