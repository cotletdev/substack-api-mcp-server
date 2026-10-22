"""Delete comment or Note."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, comment_id

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "comment_id": {"type": "string", "description": "ID of your comment, Note or Note reply."},
    },
    "required": ["comment_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"comment_id": "364150154", "deleted": True}


@tool(
    name="delete_comment",
    title="Delete comment or Note",
    access="write",
    confirm=True,
    description="Delete one of your own comments, Notes or Note replies.",
    details=(
        "Deletes something you wrote: a comment under a post, a Note or a reply to a Note. Replies other "
        "people wrote under it stay, under a deleted placeholder. Someone else's comment returns an error; "
        "on your own posts remove it with remove_comment. By default you confirm each call; you can switch "
        "that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /comments/{comment_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def delete_comment(ctx: ToolContext, args: dict[str, Any]) -> Any:

    cid = comment_id(args["comment_id"])
    await call(ctx, "DELETE", f"{WEB}/api/v1/comment/{cid}")
    return {"comment_id": str(cid), "deleted": True}
