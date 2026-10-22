"""List sections."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "sections": [
        {
            "section_id": "482783",
            "name": "Field notes",
            "description": "Short notes from the week.",
            "slug": "field-notes",
            "live": True,
            "subscribed_by_default": True,
        }
    ]
}


@tool(
    name="list_sections",
    title="List sections",
    access="read",
    confirm=False,
    description="Sections of your publication, the separate newsletters inside it.",
    details=(
        "Returns each section with its ID, name, description and slug. live is false while Substack still "
        "sets a new section up. subscribed_by_default tells whether new subscribers get its emails. A "
        "publication without sections returns an empty list."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /sections",
    example_response=EXAMPLE_RESPONSE,
)
async def list_sections(ctx: ToolContext, _args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    rows = await call(ctx, "GET", f"{pub['base']}/api/v1/publication/sections")
    return {
        "sections": [
            {
                "section_id": str(row["id"]),
                "name": row.get("name") or "",
                "description": row.get("description") or "",
                "slug": row.get("slug") or "",
                "live": bool(row.get("is_live")),
                "subscribed_by_default": bool(row.get("is_default_on")),
            }
            for row in rows or []
        ]
    }
