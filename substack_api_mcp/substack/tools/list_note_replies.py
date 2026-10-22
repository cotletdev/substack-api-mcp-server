"""List Note replies."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, comment_id, person

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "note_id": {"type": "string", "description": "Note ID from list_notes or search_substack."},
        "cursor": {"type": "string", "description": "next_cursor from the previous page."},
    },
    "required": ["note_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "replies": [
        {
            "note_id": "364150283",
            "author": {"user_id": "81309935", "name": "Sam Ortiz", "handle": ""},
            "body": "Same here, the phone rule changed everything.",
            "published_at": "2026-10-18T15:55:08.644Z",
            "likes": 2,
            "restacks": 0,
            "replies": 1,
            "url": None,
        }
    ],
    "next_cursor": None,
}


@tool(
    name="list_note_replies",
    title="List Note replies",
    access="read",
    confirm=False,
    description="Replies under a Note, with author, text and likes.",
    details=(
        "Returns the direct replies under one Note (yours or anyone's), in Substack's order. replies is the "
        "count under each reply; list those by passing its note_id. Substack sends no handle with replies, so "
        "author.handle is empty and url is null. Page with next_cursor."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /notes/{note_id}/replies",
    example_response=EXAMPLE_RESPONSE,
)
async def list_note_replies(ctx: ToolContext, args: dict[str, Any]) -> Any:

    nid = comment_id(args["note_id"], "list_notes")
    params = {"cursor": args["cursor"]} if args.get("cursor") else None
    answer = await call(ctx, "GET", f"{WEB}/api/v1/reader/comment/{nid}/replies", params=params)
    replies = [
        _note(branch["comment"])
        for branch in answer.get("commentBranches") or []
        if (branch.get("comment") or {}).get("id")
    ]
    return {"replies": replies, "next_cursor": answer.get("nextCursor")}


def _note(comment: dict[str, Any]) -> dict[str, Any]:
    handle = comment.get("handle") or ""
    return {
        "note_id": str(comment["id"]),
        "author": person({"id": comment.get("user_id"), "name": comment.get("name"), "handle": handle}),
        "body": comment.get("body") or "",
        "published_at": comment.get("date"),
        "likes": int(comment.get("reaction_count") or 0),
        "restacks": int(comment.get("restacks") or 0),
        "replies": int(comment.get("children_count") or 0),
        "url": f"{WEB}/@{handle}/note/c-{comment['id']}" if handle else None,
    }
