"""Tag post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, post_id, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "post_id": {"type": "string", "description": "Post ID from list_posts."},
        "tag_id": {"type": "string", "description": "Tag ID from list_post_tags or create_post_tag."},
        "remove": {"type": "boolean", "description": "Take the tag off instead. Default: false."},
    },
    "required": ["post_id", "tag_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "148213977",
    "tag_id": "80ba205f-6de0-4024-860d-0df42720d32a",
    "tagged": True,
}


@tool(
    name="tag_post",
    title="Tag post",
    access="write",
    confirm=False,
    description="Add a tag to a post, or take it off.",
    details=(
        "Puts one of your post tags on a draft or published post, or removes it with remove. A post can have "
        "several tags. Tagging twice keeps one tag."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /posts/{post_id}/tags/{tag_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def tag_post(ctx: ToolContext, args: dict[str, Any]) -> Any:

    tag_id = str(args["tag_id"]).strip()
    if not tag_id or "/" in tag_id:
        raise ToolError("tag_id must be the ID from list_post_tags.", ErrorCode.INVALID_INPUT)
    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    remove = bool(args.get("remove"))
    await call(ctx, "DELETE" if remove else "POST", f"{pub['base']}/api/v1/post/{pid}/tag/{tag_id}")
    return {"post_id": str(pid), "tag_id": tag_id, "tagged": not remove}
