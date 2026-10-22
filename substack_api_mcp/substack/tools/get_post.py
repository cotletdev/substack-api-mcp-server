"""Get post."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import (
    body_doc,
    draft,
    post_id,
    post_status,
    post_url,
    publication,
    scheduled_at,
)
from substack_api_mcp.substack.markdown import to_markdown

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"post_id": {"type": "string", "description": "Post ID from list_posts."}},
    "required": ["post_id"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "post_id": "148213977",
    "title": "The quiet launch",
    "subtitle": "What waiting taught me",
    "body_markdown": "Last month I shipped without telling anyone...",
    "audience": "everyone",
    "status": "published",
    "published_at": "2026-10-06T12:00:00Z",
    "url": "https://yourname.substack.com/p/the-quiet-launch",
}


@tool(
    name="get_post",
    title="Get post",
    access="read",
    confirm=False,
    description="Full post: title, subtitle, body as Markdown, audience, URL and dates.",
    details=(
        "Returns one post of your publication, draft, scheduled or published, with its full body as Markdown, "
        "including the paywalled part. Images come back as URLs. Buttons, embeds and footnotes come back as "
        "plain text, so writing the body back with update_draft drops them. A scheduled post also has "
        "publish_at."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /posts/{post_id}",
    example_response=EXAMPLE_RESPONSE,
)
async def get_post(ctx: ToolContext, args: dict[str, Any]) -> Any:

    pub = await publication(ctx)
    post = await draft(ctx, pub, post_id(args["post_id"]))
    published = bool(post.get("is_published"))
    status = post_status(post)
    answer = {
        "post_id": str(post["id"]),
        "title": (post.get("title") if published else None) or post.get("draft_title") or "",
        "subtitle": (post.get("subtitle") if published else None) or post.get("draft_subtitle") or "",
        "body_markdown": to_markdown(body_doc(post)),
        "audience": post.get("audience"),
        "status": status,
        "published_at": post.get("post_date") if published else None,
        "url": post_url(pub, post),
    }
    if status == "scheduled":
        answer["publish_at"] = scheduled_at(post)
    return answer
