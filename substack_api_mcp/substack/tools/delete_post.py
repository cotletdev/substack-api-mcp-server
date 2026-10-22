"""Delete post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, draft, post_id, publication

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

EXAMPLE_RESPONSE: dict[str, Any] = {"post_id": "148213977", "title": "Notes on slow mornings", "deleted": True}


@tool(
    name="delete_post",
    title="Delete post",
    access="write",
    confirm=True,
    description="Delete a draft, scheduled or published post, with its comments.",
    details=(
        "Deletes one post of your publication for good: a draft, a scheduled post (its send is cancelled) or "
        "a published post, which leaves the web, the archive and the app with its comments and stats. Emails "
        "already sent stay in inboxes. Substack has no undo; unpublish_post keeps the post as a draft instead. "
        "By default you confirm each call; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /posts/{post_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def delete_post(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    post = await draft(ctx, pub, pid)
    await call(ctx, "DELETE", f"{pub['base']}/api/v1/drafts/{pid}")
    return {"post_id": str(pid), "title": post.get("title") or post.get("draft_title") or "", "deleted": True}
