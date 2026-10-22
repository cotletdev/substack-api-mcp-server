"""Schedule post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, draft, post_id, publication, require_draft
from substack_api_mcp.substack.publishing import check_ready, future_time, set_options

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "post_id": {"type": "string", "description": "Post ID from list_posts."},
        "publish_at": {"type": "string", "format": "date-time", "description": "ISO 8601 with time zone."},
        "send_email": {"type": "boolean", "description": "Email it to subscribers. Default: true."},
        "section_id": {
            "type": "string",
            "description": "Section ID from list_sections, or main. Default: the draft's section, else main.",
        },
    },
    "required": ["post_id", "publish_at"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "148420031",
    "status": "scheduled",
    "publish_at": "2026-10-13T08:00:00-04:00",
    "audience": "everyone",
    "url": "https://yourname.substack.com/p/notes-on-pricing",
}


@tool(
    name="schedule_post",
    title="Schedule post",
    access="write",
    confirm=True,
    description="Publish a draft at a set time, on the web and by email.",
    details=(
        "Schedules a draft to go live at the time you set, on the web and, unless send_email is false, by email, "
        "to the audience set on the draft. The time needs a time zone and must be in the future. Substack's own "
        "pre-publish check runs first; a missing title or an empty body stops the call. A scheduled post stays "
        "editable until it goes out. On a publication with sections the post goes to section_id, else to the "
        "section already set on the draft, else to the main publication. By default you confirm each call; you "
        "can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /posts/{post_id}/schedule",
    example_response=EXAMPLE_RESPONSE,
)
async def schedule_post(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    pid = post_id(args["post_id"])
    when = future_time(args["publish_at"])
    post = await draft(ctx, pub, pid)
    require_draft(post)
    send_email = args.get("send_email", True)
    await set_options(ctx, pub, post, send_email, args.get("section_id"))
    trigger_at = when.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    await check_ready(ctx, pub, pid, trigger_at)
    audience = post.get("audience") or "everyone"
    release = {"trigger_at": trigger_at, "post_audience": audience, "email_audience": audience}
    await call(ctx, "POST", f"{pub['base']}/api/v1/drafts/{pid}/scheduled_release", body=release)
    scheduled = await draft(ctx, pub, pid)
    slug = scheduled.get("slug")
    return {
        "post_id": str(pid),
        "status": "scheduled",
        "publish_at": args["publish_at"],
        "audience": audience,
        "url": f"{pub['base']}/p/{slug}" if slug else None,
    }
