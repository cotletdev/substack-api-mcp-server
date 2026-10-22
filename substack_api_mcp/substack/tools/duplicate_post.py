"""Duplicate post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, post_id, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "post_id": {"type": "string", "description": "Post ID from list_posts."},
    },
    "required": ["post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "148214502",
    "source_post_id": "148213977",
    "title": "[COPY] Notes on slow mornings",
    "edit_url": "https://yourname.substack.com/publish/post/148214502",
}


@tool(
    name="duplicate_post",
    title="Duplicate post",
    access="write",
    confirm=False,
    description="Copy any post into a new draft.",
    details=(
        "Makes a new draft with the title, subtitle, body and settings of a draft or published post, as "
        "Duplicate in the post list does. Substack puts [COPY] in front of the title; change it with "
        "update_draft. Nothing is published or sent."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /posts/{post_id}/duplicate",
    example_response=EXAMPLE_RESPONSE,
)
async def duplicate_post(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    copy = await call(ctx, "POST", f"{pub['base']}/api/v1/posts/{pid}/duplicate")
    return {
        "post_id": str(copy["id"]),
        "source_post_id": str(pid),
        "title": copy.get("draft_title") or "",
        "edit_url": f"{pub['base']}/publish/post/{copy['id']}",
    }
