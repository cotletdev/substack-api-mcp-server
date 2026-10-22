"""Unpublish post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
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

EXAMPLE_RESPONSE: dict[str, Any] = {"post_id": "148213977", "status": "draft"}


@tool(
    name="unpublish_post",
    title="Unpublish post",
    access="write",
    confirm=True,
    description="Take a published post off the web and back to drafts.",
    details=(
        "Turns a published post back into a draft, as Unpublish in the editor does: it leaves your site, "
        "archive and the Substack app, and its link stops working. Comments and stats stay with the draft. "
        "Emails already sent stay in inboxes. Publish it again with publish_post. A post that is not published "
        "returns an error. By default you confirm each call; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /posts/{post_id}/publish",
    example_response=EXAMPLE_RESPONSE,
)
async def unpublish_post(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    post = await draft(ctx, pub, pid)
    if not post.get("is_published"):
        raise ToolError("This post is not published.", ErrorCode.INVALID_INPUT)
    await call(ctx, "POST", f"{pub['base']}/api/v1/drafts/{pid}/unpublish", body={})
    return {"post_id": str(pid), "status": "draft"}
