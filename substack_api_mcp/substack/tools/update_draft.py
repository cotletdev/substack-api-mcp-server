"""Update draft."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import byline, call, draft, post_id, publication, require_draft
from substack_api_mcp.substack.markdown import to_doc

_FIELDS = ("title", "subtitle", "body_markdown", "audience")
_AUDIENCES = ("everyone", "only_paid", "founding")

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "post_id": {"type": "string", "description": "Post ID from list_posts."},
        "fields": {
            "type": "string",
            "description": (
                'JSON object with any of title, subtitle, body_markdown, audience, e.g. {"title": "New title"}.'
            ),
        },
    },
    "required": ["post_id", "fields"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"post_id": "148420031", "status": "draft", "updated": ["title", "body_markdown"]}


@tool(
    name="update_draft",
    title="Update draft",
    access="write",
    confirm=False,
    description="Change the title, subtitle, body or audience of a draft.",
    details=(
        "Changes the fields you pass and leaves the others as they are. body_markdown replaces the whole "
        "body. Drafts and scheduled posts only: a published post returns an error. Nothing reaches your "
        "subscribers, so it runs without asking."
    ),
    input_schema=INPUT_SCHEMA,
    route="PATCH /drafts/{post_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def update_draft(ctx: ToolContext, args: dict[str, Any]) -> Any:

    fields = _fields(args["fields"])
    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    post = await draft(ctx, pub, pid)
    require_draft(post)
    body = {
        "draft_title": fields.get("title", post.get("draft_title") or ""),
        "draft_subtitle": fields.get("subtitle", post.get("draft_subtitle") or ""),
        "draft_body": json.dumps(to_doc(fields["body_markdown"]))
        if "body_markdown" in fields
        else post.get("draft_body"),
        "draft_bylines": byline(pub),
        "audience": fields.get("audience", post.get("audience") or "everyone"),
        "last_updated_at": post.get("draft_updated_at"),
    }
    await call(ctx, "PUT", f"{pub['base']}/api/v1/drafts/{pid}", body=body)
    return {"post_id": str(pid), "status": "draft", "updated": [name for name in _FIELDS if name in fields]}


def _fields(value: Any) -> dict[str, Any]:
    """`fields` is a JSON object with any of title, subtitle, body_markdown, audience."""
    parsed = value if isinstance(value, dict) else None
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except ValueError:
            parsed = None
    if not isinstance(parsed, dict) or not parsed:
        raise ToolError(
            'fields must be a JSON object, e.g. {"title": "...", "body_markdown": "..."}.', ErrorCode.INVALID_INPUT
        )
    if unknown := sorted(set(parsed) - set(_FIELDS)):
        raise ToolError(
            f"Unknown fields: {', '.join(unknown)}. Allowed: {', '.join(_FIELDS)}.", ErrorCode.INVALID_INPUT
        )
    if "audience" in parsed and parsed["audience"] not in _AUDIENCES:
        raise ToolError(f"audience must be one of {', '.join(_AUDIENCES)}.", ErrorCode.INVALID_INPUT)
    if any(not isinstance(text, str) for text in parsed.values()):
        raise ToolError("Every field value must be text.", ErrorCode.INVALID_INPUT)
    return parsed
