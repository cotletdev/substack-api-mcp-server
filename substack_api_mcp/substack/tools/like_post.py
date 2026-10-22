"""Like post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, post_id

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "post_id": {"type": "string", "description": "Post ID from search_substack, list_posts or a post's data."},
        "unlike": {"type": "boolean", "description": "Remove your like instead. Default: false."},
    },
    "required": ["post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"post_id": "197396217", "liked": True}


@tool(
    name="like_post",
    title="Like post",
    access="write",
    confirm=False,
    description="Like or unlike any Substack post as you.",
    details=(
        "Adds your heart to a post on any publication, as the heart under a post does, or removes it with "
        "unlike. The author sees your like in their activity. Liking twice keeps one like."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /posts/{post_id}/like",
    example_response=EXAMPLE_RESPONSE,
)
async def like_post(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pid = post_id(args["post_id"])
    unlike = bool(args.get("unlike"))
    await call(ctx, "DELETE" if unlike else "POST", f"{WEB}/api/v1/post/{pid}/reaction", body={"reaction": "\u2764"})
    return {"post_id": str(pid), "liked": not unlike}
