"""Publish Note."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, draft, post_id, post_url, publication
from substack_api_mcp.substack.markdown import to_note_doc
from substack_api_mcp.substack.publishing import future_time

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "body": {"type": "string", "description": "Note text, up to 1,000 characters."},
        "link_post_id": {"type": "string", "description": "Attach one of your published posts as a link card."},
        "publish_at": {
            "type": "string",
            "format": "date-time",
            "description": "ISO 8601 with time zone. Omit to post now.",
        },
    },
    "required": ["body"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "note_id": "5521098",
    "status": "published",
    "published_at": "2026-10-11T10:05:00Z",
    "url": "https://substack.com/@yourname/note/c-5521098",
}


@tool(
    name="publish_note",
    title="Publish Note",
    access="write",
    confirm=True,
    description=(
        "Short post in Substack Notes, now or at a set time, optionally with a link card to one of your posts."
    ),
    details=(
        "Posts a Note under your name. Without publish_at it goes out now; with it, the Note waits in your "
        "scheduled Notes, status is scheduled and published_at is that time. Text is 1 to 1,000 characters. "
        "link_post_id must be a published post. By default you confirm each call; you can switch that off "
        "for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /notes",
    example_response=EXAMPLE_RESPONSE,
)
async def publish_note(ctx: ToolContext, args: dict[str, Any]) -> Any:

    text = args["body"].strip()
    if not text or len(text) > 1000:
        raise ToolError("body must be 1 to 1,000 characters.", ErrorCode.INVALID_INPUT)
    pub = await publication(ctx)
    doc = to_note_doc(text)
    note: dict[str, Any] = {"bodyJson": doc, "tabId": "for-you", "surface": "feed", "replyMinimumRole": "everyone"}
    if args.get("link_post_id"):
        url = post_url(pub, await draft(ctx, pub, post_id(args["link_post_id"])))
        if not url:
            raise ToolError("link_post_id must be a published post.", ErrorCode.INVALID_INPUT)
        card = await call(ctx, "POST", f"{WEB}/api/v1/comment/attachment", body={"url": url, "type": "link"})
        note["attachmentIds"] = [card["id"]]
    if args.get("publish_at"):
        # A scheduled Note is a draft Note with its time: Notes > Scheduled.
        note["trigger_at"] = future_time(args["publish_at"]).strftime("%Y-%m-%dT%H:%M:%S.000Z")
        saved = await call(ctx, "POST", f"{WEB}/api/v1/comment/draft", body=note)
    else:
        saved = await call(ctx, "POST", f"{WEB}/api/v1/comment/feed", body=note)
    scheduled = bool(args.get("publish_at"))
    return {
        "note_id": str(saved["id"]),
        "status": "scheduled" if scheduled else "published",
        "published_at": args["publish_at"] if scheduled else saved.get("date"),
        "url": f"{WEB}/@{pub['handle']}/note/c-{saved['id']}",
    }
