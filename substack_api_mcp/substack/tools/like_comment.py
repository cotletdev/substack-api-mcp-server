"""Like comment."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, comment_id, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "comment_id": {"type": "string", "description": "Comment ID from list_comments, or a Note ID."},
        "unlike": {"type": "boolean", "description": "Remove your like instead. Default: false."},
    },
    "required": ["comment_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"comment_id": "364149469", "liked": True}


@tool(
    name="like_comment",
    title="Like comment or Note",
    access="write",
    confirm=False,
    description="Like or unlike a comment or a Note as you.",
    details=(
        "Adds your heart to any Note or Note reply, or to a comment under a post of your publication, or "
        "removes it with unlike. Comments and Notes share one ID space, so a Note ID from list_notes or "
        "search_substack works too. The author sees your like in their activity."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /comments/{comment_id}/like",
    example_response=EXAMPLE_RESPONSE,
)
async def like_comment(ctx: ToolContext, args: dict[str, Any]) -> Any:

    cid = comment_id(args["comment_id"])
    unlike = bool(args.get("unlike"))
    method = "DELETE" if unlike else "POST"
    try:
        # Notes and their replies live on substack.com.
        await call(ctx, method, f"{WEB}/api/v1/comment/{cid}/reaction", body={"reaction": "\u2764"})
    except ToolError as exc:
        if exc.code != ErrorCode.TARGET_ERROR:
            raise
        # A comment under a post answers only on its publication's host, as the post page sends it.
        pub = await publication(ctx)
        body = {"publication_id": pub["id"], "reaction": "\u2764"}
        await call(ctx, method, f"{pub['base']}/api/v1/comment/{cid}/reaction", body=body)
    return {"comment_id": str(cid), "liked": not unlike}
