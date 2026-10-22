"""Create draft."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import byline, call, publication
from substack_api_mcp.substack.markdown import to_doc

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "title": {"type": "string", "description": "Post title."},
        "body_markdown": {"type": "string", "description": "Post body in Markdown. Images by public URL."},
        "subtitle": {"type": "string", "description": "Shown under the title and in the email preview."},
        "audience": {
            "type": "string",
            "enum": ["everyone", "only_paid", "founding"],
            "description": "everyone, only_paid or founding. Default: everyone.",
        },
    },
    "required": ["title", "body_markdown"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "148420031",
    "status": "draft",
    "audience": "everyone",
    "edit_url": "https://yourname.substack.com/publish/post/148420031",
}


@tool(
    name="create_draft",
    title="Create draft",
    access="write",
    confirm=False,
    description="New draft from Markdown. Nothing is sent until you publish or schedule it.",
    details=(
        "Creates a draft in your publication and returns its post_id and editor link. Markdown covers "
        "headings, paragraphs, bullet and numbered lists, quotes, code blocks, rules, images by public URL, "
        "bold, italic, strikethrough, inline code and links; local image files cannot be used. Sending is a "
        "separate step: schedule_post or publish_post. A draft reaches no one, so it runs without asking."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /drafts",
    example_response=EXAMPLE_RESPONSE,
)
async def create_draft(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    audience = args.get("audience") or "everyone"
    body = {
        "draft_title": args["title"],
        "draft_subtitle": args.get("subtitle") or "",
        "draft_body": json.dumps(to_doc(args["body_markdown"])),
        "draft_bylines": byline(pub),
        "audience": audience,
        "type": "newsletter",
        "section_chosen": False,
        "draft_section_id": None,
    }
    post = await call(ctx, "POST", f"{pub['base']}/api/v1/drafts", body=body)
    return {
        "post_id": str(post["id"]),
        "status": "draft",
        "audience": post.get("audience") or audience,
        "edit_url": f"{pub['base']}/publish/post/{post['id']}",
    }
