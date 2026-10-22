"""Create post tag."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"name": {"type": "string", "description": "Tag name, e.g. Habits."}},
    "required": ["name"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "tag_id": "80ba205f-6de0-4024-860d-0df42720d32a",
    "name": "Habits",
    "slug": "habits",
}


@tool(
    name="create_post_tag",
    title="Create post tag",
    access="write",
    confirm=False,
    description="New tag for grouping your posts.",
    details=(
        "Creates a post tag on your publication; Substack makes the slug from the name. A tag with no posts "
        "shows nowhere. Put posts under it with tag_post."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /post-tags",
    example_response=EXAMPLE_RESPONSE,
)
async def create_post_tag(ctx: ToolContext, args: dict[str, Any]) -> Any:

    name = str(args["name"]).strip()
    if not name or len(name) > 100:
        raise ToolError("name must be 1 to 100 characters.", ErrorCode.INVALID_INPUT)
    pub = await publication(ctx)
    tag = await call(ctx, "POST", f"{pub['base']}/api/v1/publication/post-tag", body={"name": name})
    return {"tag_id": str(tag["id"]), "name": tag.get("name") or name, "slug": tag.get("slug") or ""}
