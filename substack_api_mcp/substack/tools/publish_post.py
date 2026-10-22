"""Publish post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, draft, post_id, publication, require_draft
from substack_api_mcp.substack.publishing import check_ready, set_options

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "post_id": {"type": "string", "description": "Post ID from list_posts."},
        "send_email": {"type": "boolean", "description": "Email it to subscribers. Default: true."},
        "section_id": {
            "type": "string",
            "description": "Section ID from list_sections, or main. Default: the draft's section, else main.",
        },
    },
    "required": ["post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "148420031",
    "status": "published",
    "published_at": "2026-10-11T10:02:00Z",
    "emailed": True,
    "url": "https://yourname.substack.com/p/notes-on-pricing",
}


@tool(
    name="publish_post",
    title="Publish post",
    access="write",
    confirm=True,
    description="Publish a draft now.",
    details=(
        "Publishes a draft immediately, on the web and, unless send_email is false, by email, to the audience set"
        " on the draft. Substack's own pre-publish check runs first; a missing title or an empty body stops the "
        "call. A sent email cannot be recalled. On a publication with sections the post goes to section_id, else "
        "to the section already set on the draft, else to the main publication. By default you confirm each call;"
        " you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /posts/{post_id}/publish",
    example_response=EXAMPLE_RESPONSE,
)
async def publish_post(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    post = await draft(ctx, pub, pid)
    require_draft(post)
    send_email = args.get("send_email", True)
    await set_options(ctx, pub, post, send_email, args.get("section_id"))
    await check_ready(ctx, pub, pid, None)
    body = {"send": send_email, "share_automatically": False}
    published = await call(ctx, "POST", f"{pub['base']}/api/v1/drafts/{pid}/publish", body=body)
    slug = published.get("slug")
    return {
        "post_id": str(pid),
        "status": "published",
        "published_at": published.get("post_date"),
        "emailed": bool(published.get("should_send_email", send_email)),
        "url": f"{pub['base']}/p/{slug}" if slug else None,
    }
