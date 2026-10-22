"""List Notes."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, person, publication, user_ref

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "user": {"type": "string", "description": "Handle (e.g. @mayachen) or user ID. Default: you."},
        "cursor": {"type": "string", "description": "next_cursor from the previous page."},
    },
    "required": [],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "notes": [
        {
            "note_id": "364150154",
            "author": {"user_id": "561078443", "name": "Maya Chen", "handle": "mayachen"},
            "body": "Day 21 of the early hour. Coffee first, phone last.",
            "published_at": "2026-10-18T15:54:57.801Z",
            "likes": 12,
            "restacks": 1,
            "replies": 3,
            "url": "https://substack.com/@mayachen/note/c-364150154",
        }
    ],
    "next_cursor": None,
}


@tool(
    name="list_notes",
    title="List Notes",
    access="read",
    confirm=False,
    description="Notes posted by you or any other Substack user, newest first, with likes and replies.",
    details=(
        "Returns the Notes on a profile's Notes tab, newest first: text, time, likes, restacks, reply count "
        "and link. Without user it lists yours. Posts and restacks of posts on the profile are left out. "
        "Page with next_cursor. Pass note_id to list_note_replies, like_comment or reply_to_note."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /notes",
    example_response=EXAMPLE_RESPONSE,
)
async def list_notes(ctx: ToolContext, args: dict[str, Any]) -> Any:

    who = await user_ref(ctx, args["user"]) if args.get("user") else {"id": (await publication(ctx))["user_id"]}
    uid = who["id"]
    params = {"cursor": args["cursor"]} if args.get("cursor") else None
    answer = await call(ctx, "GET", f"{WEB}/api/v1/reader/feed/profile/{uid}", params=params)
    notes = [
        _note(item["comment"])
        for item in answer.get("items") or []
        if item.get("type") == "comment" and (item.get("comment") or {}).get("id")
    ]
    return {"notes": notes, "next_cursor": answer.get("nextCursor")}


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
