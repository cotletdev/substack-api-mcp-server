"""Substack web requests recorded on a test publication (17.10.2026).

Two hosts, both with the account's own cookies (`substack.sid` on .substack.com):
- `substack.com/api/v1`: the reader app (who am I, Notes, comment lookup).
- `{subdomain}.substack.com/api/v1`: the publisher dashboard of one publication (posts, drafts, stats,
  subscribers, comments). Requests go to the subdomain even when the publication has a custom domain:
  the custom domain is outside the manifest's domains, and Substack answers the same on both.
The tools work on the account's own publication: the first one it administers, as the dashboard opens it.
Answers keep Substack's ids as strings; times are ISO 8601 as Substack sends them. Cursors are offsets.
"""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, TargetBlockedError, ToolError
from substack_api_mcp.core.helpers import json_field, page_cursor

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

WEB = "https://substack.com"
_PUBLISHER_ROLES = ("admin", "owner", "editor", "contributor")
# The preloads are a JSON string inside the page, so the quotes may come escaped.
_BANNED = re.compile(r'is_globally_banned\\*"\s*:\s*true')


async def me(ctx: ToolContext) -> dict[str, Any]:
    """The signed-in user's profile with their publications (`publicationUsers`)."""
    return await call(ctx, "GET", f"{WEB}/api/v1/user/profile/self")


async def publication(ctx: ToolContext) -> dict[str, Any]:
    """The account's own publication: ids, base URL of its dashboard API and the author's byline id."""
    profile = await me(ctx)
    for row in profile.get("publicationUsers") or []:
        pub = row.get("publication") or {}
        if row.get("role") in _PUBLISHER_ROLES and pub.get("subdomain"):
            return {
                "id": pub.get("id"),
                "name": pub.get("name"),
                "subdomain": pub["subdomain"],
                "base": f"https://{pub['subdomain']}.substack.com",
                "user_id": profile.get("id"),
                "handle": profile.get("handle"),
                "role": row.get("role"),
            }
    if await _suspended(ctx):
        raise TargetBlockedError(
            "Substack suspended this account and hid its publication. The notice and the appeal link are on "
            "substack.com in your Cloud Browser."
        )
    raise ToolError("This Substack account has no publication it can publish to.", ErrorCode.APP_PERMISSION_DENIED)


async def _suspended(ctx: ToolContext) -> bool:
    """A suspended account still signs in, but its profile lists no publications (18.10.2026).

    Only the page's preloaded user says why (`is_globally_banned`); no JSON endpoint carries it.
    """
    response = await ctx.call("GET", f"{WEB}/", headers={"accept": "text/html"})
    return bool(_BANNED.search(response.text))


async def call(
    ctx: ToolContext, method: str, url: str, *, params: dict[str, Any] | None = None, body: Any = None
) -> Any:
    """One Substack API request; errors become messages for the agent."""
    host = url.split("/api/")[0]
    headers = {"referer": f"{host}/", "origin": host, "accept": "application/json"}
    response = await ctx.call(method, url, params=params, json=body, headers=headers)
    if response.status == 404:
        raise ToolError("Substack has no such item, or this account cannot see it.", ErrorCode.TARGET_ERROR)
    if response.status == 429:
        raise ToolError("Substack is limiting this account; try again in a few minutes.", ErrorCode.RATE_LIMITED)
    if response.status >= 400:
        raise ToolError(f"Substack refused the request ({response.status}).", ErrorCode.TARGET_ERROR)
    if not response.text.strip():
        return {}
    try:
        return response.json()
    except ValueError as exc:
        raise ToolError("Substack answered with a page instead of data.", ErrorCode.TARGET_ERROR) from exc


def offset_cursor(cursor: str | None) -> int:
    """Offsets as cursors: none is the first page, anything else is a next_cursor we handed out."""
    return page_cursor(cursor) if cursor else 0


def next_cursor(offset: int, got: int, wanted: int) -> str | None:
    return str(offset + got) if got >= wanted else None


def comment_id(value: Any, source: str = "list_comments") -> int:
    """Comments and Notes share one ID space; Note URLs prefix it with c-."""
    text = str(value or "").strip().removeprefix("c-")
    if not text.isdigit():
        raise ToolError(f"comment_id must be the numeric ID from {source}.", ErrorCode.INVALID_INPUT)
    return int(text)


async def user_ref(ctx: ToolContext, value: Any) -> dict[str, Any]:
    """A Substack user by numeric ID or handle (with or without @): id, name and handle."""
    text = str(value or "").strip().removeprefix("@")
    if not re.fullmatch(r"[A-Za-z0-9_]{1,80}", text):
        raise ToolError("user must be a Substack handle or a numeric user ID.", ErrorCode.INVALID_INPUT)
    if text.isdigit():
        # Profiles are looked up by handle only; a numeric ID goes straight to the request.
        return {"id": int(text), "name": "", "handle": ""}
    found = await call(ctx, "GET", f"{WEB}/api/v1/user/{text}/public_profile")
    return {"id": int(found["id"]), "name": found.get("name") or "", "handle": found.get("handle") or ""}


def person(user: dict[str, Any] | None) -> dict[str, Any]:
    """Who someone is in our answers: never their email."""
    user = user or {}
    return {
        "user_id": str(user.get("id") or user.get("user_id") or ""),
        "name": user.get("name") or "",
        "handle": user.get("handle") or "",
    }


def post_id(value: Any) -> int:
    text = str(value or "").strip()
    if not text.isdigit():
        raise ToolError("post_id must be the numeric ID from list_posts.", ErrorCode.INVALID_INPUT)
    return int(text)


def post_status(post: dict[str, Any]) -> str:
    if post.get("is_published"):
        return "published"
    if post.get("trigger_at") or post.get("postSchedules"):
        return "scheduled"
    return "draft"


def post_url(pub: dict[str, Any], post: dict[str, Any]) -> str | None:
    if not post.get("is_published") or not post.get("slug"):
        return None
    return post.get("canonical_url") or f"{pub['base']}/p/{post['slug']}"


def scheduled_at(post: dict[str, Any]) -> str | None:
    if post.get("trigger_at"):
        return post["trigger_at"]
    schedules = post.get("postSchedules") or []
    return schedules[0].get("trigger_at") if schedules else None


async def draft(ctx: ToolContext, pub: dict[str, Any], pid: int) -> dict[str, Any]:
    """The editor's copy of a post: drafts, scheduled and published posts alike (body in `body`/`draft_body`)."""
    return await call(ctx, "GET", f"{pub['base']}/api/v1/drafts/{pid}")


def require_draft(post: dict[str, Any]) -> None:
    if post.get("is_published"):
        raise ToolError("This post is already published; only drafts can be changed here.", ErrorCode.INVALID_INPUT)


def body_doc(post: dict[str, Any]) -> dict[str, Any]:
    """The post's ProseMirror document: the published body, else the draft's."""
    raw = post.get("body") if post.get("is_published") and post.get("body") else post.get("draft_body")
    doc = json_field(raw)
    return doc if isinstance(doc, dict) else {"type": "doc", "content": []}


def byline(pub: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"id": pub["user_id"], "is_guest": False}]
