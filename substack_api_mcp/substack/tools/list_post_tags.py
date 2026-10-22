"""List post tags."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "tags": [{"tag_id": "80ba205f-6de0-4024-860d-0df42720d32a", "name": "Habits", "slug": "habits", "hidden": False}]
}


@tool(
    name="list_post_tags",
    title="List post tags",
    access="read",
    confirm=False,
    description="Tags your publication uses to group posts.",
    details=(
        "Returns every post tag of your publication with its ID, name and slug; readers see tagged posts on "
        "/t/{slug}. hidden tags group posts without a public page. Pass tag_id to tag_post."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /post-tags",
    example_response=EXAMPLE_RESPONSE,
)
async def list_post_tags(ctx: ToolContext, _args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    rows = await call(ctx, "GET", f"{pub['base']}/api/v1/publication/post-tag")
    return {
        "tags": [
            {
                "tag_id": str(row["id"]),
                "name": row.get("name") or "",
                "slug": row.get("slug") or "",
                "hidden": bool(row.get("hidden")),
            }
            for row in rows or []
        ]
    }
