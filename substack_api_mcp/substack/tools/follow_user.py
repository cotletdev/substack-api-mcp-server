"""Follow user."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, user_ref

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "user": {"type": "string", "description": "Handle (e.g. @mayachen) or user ID."},
        "unfollow": {"type": "boolean", "description": "Unfollow instead. Default: false."},
    },
    "required": ["user"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"user_id": "41856304", "handle": "mayachen", "following": True}


@tool(
    name="follow_user",
    title="Follow user",
    access="write",
    confirm=False,
    description="Follow or unfollow a Substack user, so their Notes reach your feed.",
    details=(
        "Follows a person on Substack, as Follow on their profile does, or unfollows them. Following is not "
        "subscribing: you get their Notes and activity in the app, not their newsletter by email. They see "
        "the follow."
    ),
    input_schema=INPUT_SCHEMA,
    route="PUT /users/{user}/follow",
    example_response=EXAMPLE_RESPONSE,
)
async def follow_user(ctx: ToolContext, args: dict[str, Any]) -> Any:

    user = await user_ref(ctx, args["user"])
    unfollow = bool(args.get("unfollow"))
    await call(ctx, "DELETE" if unfollow else "POST", f"{WEB}/api/v1/feed/{user['id']}/follow")
    return {"user_id": str(user["id"]), "handle": user["handle"], "following": not unfollow}
