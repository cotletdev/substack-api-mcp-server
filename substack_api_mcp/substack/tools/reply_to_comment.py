"""Reply to comment."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "comment_id": {"type": "string", "description": "Comment ID from list_comments."},
        "body": {"type": "string", "description": "Reply text."},
    },
    "required": ["comment_id", "body"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "comment_id": "363485182",
    "parent_id": "363478059",
    "created_at": "2026-10-11T10:07:00Z",
}


@tool(
    name="reply_to_comment",
    title="Reply to comment",
    access="write",
    confirm=True,
    description="Reply as you under a comment on your post.",
    details=(
        "Posts a reply under one comment on a post of your publication, under your name, visible to everyone "
        "who can read the post. A comment elsewhere on Substack returns an error. The author gets Substack's "
        "usual reply notification. By default you confirm each call; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /comments/{comment_id}/replies",
    example_response=EXAMPLE_RESPONSE,
)
async def reply_to_comment(ctx: ToolContext, args: dict[str, Any]) -> Any:

    comment_id = str(args["comment_id"]).strip().removeprefix("c-")
    if not comment_id.isdigit():
        raise ToolError("comment_id must be the ID from list_comments.", ErrorCode.INVALID_INPUT)
    text = args["body"].strip()
    if not text:
        raise ToolError("body must not be empty.", ErrorCode.INVALID_INPUT)
    pub = await publication(ctx)
    found = await call(ctx, "GET", f"{pub['base']}/api/v1/reader/comment/{comment_id}")
    parent = (found.get("item") or {}).get("comment") or {}
    if not parent.get("post_id"):
        raise ToolError("Substack has no comment with this ID.", ErrorCode.TARGET_ERROR)
    if parent.get("publication_id") != pub["id"]:
        raise ToolError("This comment is not on a post of your publication.", ErrorCode.APP_PERMISSION_DENIED)
    body = {"body": text, "parent_id": int(comment_id)}
    reply = await call(ctx, "POST", f"{pub['base']}/api/v1/post/{parent['post_id']}/comment", body=body)
    return {"comment_id": str(reply["id"]), "parent_id": comment_id, "created_at": reply.get("date")}
