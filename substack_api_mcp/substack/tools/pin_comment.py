"""Pin comment."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, comment_id, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "comment_id": {"type": "string", "description": "Comment ID from list_comments."},
        "unpin": {"type": "boolean", "description": "Unpin instead. Default: false."},
    },
    "required": ["comment_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"comment_id": "364149469", "pinned": True}


@tool(
    name="pin_comment",
    title="Pin comment",
    access="write",
    confirm=False,
    description="Pin a comment to the top of your post's comments, or unpin it.",
    details=(
        "Pins one comment on a post of your publication above all others, as Pin in the comment menu does, "
        "or unpins it. A comment on someone else's post returns an error."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /comments/{comment_id}/pin",
    example_response=EXAMPLE_RESPONSE,
)
async def pin_comment(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    cid = comment_id(args["comment_id"])
    pinned = not args.get("unpin")
    await call(ctx, "PATCH", f"{pub['base']}/api/v1/comment/{cid}/pin", body={"pinned": pinned})
    return {"comment_id": str(cid), "pinned": pinned}
