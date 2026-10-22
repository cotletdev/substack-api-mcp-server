"""Export subscribers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import publication
from substack_api_mcp.substack.subscribers import export

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {"type": "object", "properties": {}, "required": [], "additionalProperties": False}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "download_url": "https://substack-post-media.s3.us-east-1.amazonaws.com/publication_export/7f3c2a.csv?X-Amz-Expires=86400&X-Amz-Signature=...",
    "rows": 4380,
    "expires_at": "2026-10-12T10:00:00+00:00",
}


@tool(
    name="export_subscribers",
    title="Export subscribers",
    access="read",
    confirm=False,
    description="The full subscriber list as a CSV download link, with the row count.",
    details=(
        "Builds the same CSV as Export in the subscriber dashboard: email, name, subscription type, activity "
        "rating and start date. Substack builds the file in the background; the call waits up to about a "
        "minute and otherwise asks you to try again later. The link needs no sign-in and works until "
        "expires_at, 24 hours when we recorded it. For filtered pages use list_subscribers."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /subscribers/export",
    example_response=EXAMPLE_RESPONSE,
)
async def export_subscribers(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    return await export(ctx, pub)
