"""Tag subscribers."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication
from substack_api_mcp.substack.subscribers import find_subscriber

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "tag_id": {"type": "string", "description": "Tag ID from list_subscriber_tags or create_subscriber_tag."},
        "emails": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
            "maxItems": 50,
            "description": "Subscribers' email addresses, up to 50.",
        },
        "remove": {"type": "boolean", "description": "Take the tag off instead. Default: false."},
    },
    "required": ["tag_id", "emails"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "tag_id": "9357",
    "tagged": True,
    "updated": ["reader@example.com"],
    "not_found": ["someone@example.com"],
}


@tool(
    name="tag_subscribers",
    title="Tag subscribers",
    access="write",
    confirm=False,
    description="Put a tag on subscribers by email, or take it off.",
    details=(
        "Adds one of your subscriber tags to up to 50 subscribers, or removes it with remove. Emails not on "
        "your list come back in not_found and nothing else fails. A subscriber added a minute ago may not be "
        "findable yet; try again shortly."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /subscriber-tags/{tag_id}/subscribers",
    example_response=EXAMPLE_RESPONSE,
)
async def tag_subscribers(ctx: ToolContext, args: dict[str, Any]) -> Any:

    tag_id = str(args["tag_id"]).strip()
    if not tag_id.isdigit():
        raise ToolError("tag_id must be the ID from list_subscriber_tags.", ErrorCode.INVALID_INPUT)
    pub = await publication(ctx)
    updated, missing, ids = [], [], []
    for email in dict.fromkeys(str(email).strip() for email in args["emails"]):
        row = await find_subscriber(ctx, pub, email) if email else None
        if row and row.get("subscription_id"):
            ids.append(row["subscription_id"])
            updated.append(row["user_email_address"])
        else:
            missing.append(email)
    remove = bool(args.get("remove"))
    if ids:
        action = "unassign" if remove else "assign"
        await call(
            ctx, "POST", f"{pub['base']}/api/v1/subscriber-tags/{tag_id}/{action}", body={"subscriptionIds": ids}
        )
    return {"tag_id": tag_id, "tagged": not remove, "updated": updated, "not_found": missing}
