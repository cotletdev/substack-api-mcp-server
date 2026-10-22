"""Steps the editor's Publish dialog takes before a post goes out, shared by publish_post and schedule_post."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.substack.client import byline, call

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext


def future_time(value: str) -> datetime:
    """An ISO 8601 time with a zone, later than now."""
    try:
        when = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ToolError("Time must be ISO 8601, e.g. 2026-10-20T08:00:00-04:00.", ErrorCode.INVALID_INPUT) from exc
    if when.tzinfo is None:
        raise ToolError("Time must include a time zone, e.g. -04:00 or Z.", ErrorCode.INVALID_INPUT)
    if when <= datetime.now(UTC):
        raise ToolError("Time must be in the future.", ErrorCode.INVALID_INPUT)
    return when.astimezone(UTC)


async def set_options(
    ctx: ToolContext, pub: dict[str, Any], post: dict[str, Any], send_email: bool, section_id: Any = None
) -> None:
    """The dialog's "Send via email" box and section choice, saved on the draft before it goes out.

    A publication with sections refuses to publish until the draft names one ("Please choose a section");
    the editor saves section_chosen with draft_section_id, null for the main publication.
    """
    section = _section(section_id)
    email_same = bool(post.get("should_send_email", True)) == send_email
    section_same = bool(post.get("section_chosen")) and (section_id is None or post.get("draft_section_id") == section)
    if email_same and section_same:
        return
    body = {
        "draft_title": post.get("draft_title") or "",
        "draft_subtitle": post.get("draft_subtitle") or "",
        "draft_body": post.get("draft_body"),
        "draft_bylines": byline(pub),
        "audience": post.get("audience") or "everyone",
        "should_send_email": send_email,
        "section_chosen": True,
        "draft_section_id": section if section_id is not None else post.get("draft_section_id"),
        "last_updated_at": post.get("draft_updated_at"),
    }
    await call(ctx, "PUT", f"{pub['base']}/api/v1/drafts/{post['id']}", body=body)


def _section(value: Any) -> int | None:
    if value is None or str(value).strip() in ("", "main"):
        return None
    text = str(value).strip()
    if not text.isdigit():
        raise ToolError("section_id must be the ID from list_sections, or main.", ErrorCode.INVALID_INPUT)
    return int(text)


async def check_ready(ctx: ToolContext, pub: dict[str, Any], pid: int, publish_date: str | None) -> None:
    """Substack's own pre-publish check; its errors (no title, empty body) stop the call, suggestions do not."""
    params = {"publish_date": publish_date} if publish_date else None
    answer = await call(ctx, "GET", f"{pub['base']}/api/v1/drafts/{pid}/prepublish", params=params)
    if errors := answer.get("errors") or []:
        names = ", ".join(str(error.get("identifier") or error.get("msg") or error) for error in errors)
        raise ToolError(f"Substack will not publish this draft yet: {names}.", ErrorCode.INVALID_INPUT)
