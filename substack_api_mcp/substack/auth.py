"""Who is signed in: Substack's own answer for the account (substack.com/api/v1/user/profile/self)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from substack_api_mcp.core.errors import AuthExpiredError
from substack_api_mcp.substack.client import WEB

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext


async def whoami(ctx: ToolContext) -> str | None:
    """None only when Substack says signed out; any other failure raises (detection tries again later)."""
    try:
        response = await ctx.call("GET", f"{WEB}/api/v1/user/profile/self", headers={"accept": "application/json"})
    except AuthExpiredError:
        return None
    if response.status != 200:
        return None
    me = response.json()
    if not me.get("id"):
        return None
    name, handle = me.get("name") or "", me.get("handle") or ""
    return f"{name} (@{handle})" if name and handle else name or (f"@{handle}" if handle else None)
