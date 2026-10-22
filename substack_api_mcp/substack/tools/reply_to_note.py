"""Reply to Note."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, comment_id
from substack_api_mcp.substack.markdown import to_note_doc

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "note_id": {"type": "string", "description": "Note ID from list_notes, list_note_replies or search_substack."},
        "body": {"type": "string", "description": "Reply text, up to 1,000 characters."},
    },
    "required": ["note_id", "body"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "note_id": "364150283",
    "parent_id": "364150154",
    "published_at": "2026-10-18T15:55:08.644Z",
}


@tool(
    name="reply_to_note",
    title="Reply to Note",
    access="write",
    confirm=True,
    description="Reply as you under any Note or Note reply.",
    details=(
        "Posts a reply under a Note (yours or anyone's) or under a reply to one, visible to everyone who "
        "sees the Note. Text is 1 to 1,000 characters; Markdown bold, italics and links work. The author gets "
        "Substack's usual notification. By default you confirm each call; you can switch that off for this "
        "tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /notes/{note_id}/replies",
    example_response=EXAMPLE_RESPONSE,
)
async def reply_to_note(ctx: ToolContext, args: dict[str, Any]) -> Any:

    parent = comment_id(args["note_id"], "list_notes")
    text = str(args["body"]).strip()
    if not text or len(text) > 1000:
        raise ToolError("body must be 1 to 1,000 characters.", ErrorCode.INVALID_INPUT)
    body = {"bodyJson": to_note_doc(text), "parent_id": parent, "replyMinimumRole": "everyone"}
    reply = await call(ctx, "POST", f"{WEB}/api/v1/comment/feed", body=body)
    return {"note_id": str(reply["id"]), "parent_id": str(parent), "published_at": reply.get("date")}
