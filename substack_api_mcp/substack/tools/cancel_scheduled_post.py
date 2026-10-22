"""Cancel scheduled post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, draft, post_id, publication, scheduled_at

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
    "post_id": "148213977",
    "status": "draft",
    "was_scheduled_for": "2026-10-20T12:00:00Z",
}


@tool(
    name="cancel_scheduled_post",
    title="Cancel scheduled post",
    access="write",
    confirm=False,
    description="Stop a scheduled post from going out; it stays as a draft.",
    details=(
        "Removes the scheduled time from a post, so nothing is published or emailed then; the post stays a "
        "draft with its content. Schedule it again with schedule_post. A post with no schedule returns an "
        "error."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /posts/{post_id}/schedule",
    example_response=EXAMPLE_RESPONSE,
)
async def cancel_scheduled_post(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    post = await draft(ctx, pub, pid)
    when = scheduled_at(post)
    if post.get("is_published") or not when:
        raise ToolError("This post is not scheduled.", ErrorCode.INVALID_INPUT)
    await call(ctx, "DELETE", f"{pub['base']}/api/v1/drafts/{pid}/scheduled_release")
    return {"post_id": str(pid), "status": "draft", "was_scheduled_for": when}
