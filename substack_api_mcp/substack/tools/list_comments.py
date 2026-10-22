"""List comments."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, post_id, publication

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "post_id": {"type": "string", "description": "Post ID from list_posts."},
        "unanswered_only": {"type": "boolean", "description": "Skip threads you already replied to."},
    },
    "required": ["post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "comments": [
        {
            "comment_id": "363478059",
            "author": "Maya Chen",
            "body": "Does the next part cover pricing?",
            "created_at": "2026-10-07T08:20:00Z",
            "replied": False,
            "replies": [],
        }
    ]
}


@tool(
    name="list_comments",
    title="List comments",
    access="read",
    confirm=False,
    description="Comments on a post, with author, text and whether you replied.",
    details=(
        "Returns all comments of one post at once, oldest first, with replies nested under their parent. "
        "Deleted comments are left out. replied is true when you answered anywhere in the thread under the "
        "comment; unanswered_only keeps only top-level comments where you did not. Pass comment_id to "
        "reply_to_comment."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /posts/{post_id}/comments",
    example_response=EXAMPLE_RESPONSE,
)
async def list_comments(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    params = {"all_comments": "true", "sort": "oldest_first"}
    answer = await call(ctx, "GET", f"{pub['base']}/api/v1/post/{pid}/comments", params=params)
    comments = [_comment(row, pub["user_id"]) for row in answer.get("comments") or [] if not row.get("deleted")]
    if args.get("unanswered_only"):
        comments = [item for item in comments if not item["replied"]]
    return {"comments": comments}


def _comment(row: dict[str, Any], me: Any) -> dict[str, Any]:
    children = [child for child in row.get("children") or [] if not child.get("deleted")]
    return {
        "comment_id": str(row["id"]),
        "author": row.get("name") or "",
        "body": row.get("body") or "",
        "created_at": row.get("date"),
        "replied": _replied(children, me),
        "replies": [_comment(child, me) for child in children],
    }


def _replied(children: list[dict[str, Any]], me: Any) -> bool:
    """Whether you answered anywhere in the thread under the comment."""
    return any(child.get("user_id") == me or _replied(child.get("children") or [], me) for child in children)
