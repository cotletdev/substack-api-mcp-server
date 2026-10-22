"""Remove comment."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, comment_id, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"comment_id": {"type": "string", "description": "Comment ID from list_comments."}},
    "required": ["comment_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"comment_id": "364149469", "status": "moderator_removed"}


@tool(
    name="remove_comment",
    title="Remove comment",
    access="write",
    confirm=True,
    description="Remove someone's comment from your post as the publication's moderator.",
    details=(
        "Hides a comment on a post of your publication, as Remove in the comment menu does: readers see "
        "that a moderator removed it, the text is gone, replies under it stay. Use delete_comment for your "
        "own comments. A comment on someone else's post returns an error. By default you confirm each call; "
        "you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /comments/{comment_id}/remove",
    example_response=EXAMPLE_RESPONSE,
)
async def remove_comment(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    cid = comment_id(args["comment_id"])
    body = {"status": "moderator_removed"}
    answer = await call(ctx, "PATCH", f"{pub['base']}/api/v1/comment/{cid}/status", body=body)
    return {"comment_id": str(cid), "status": answer.get("status") or "moderator_removed"}
