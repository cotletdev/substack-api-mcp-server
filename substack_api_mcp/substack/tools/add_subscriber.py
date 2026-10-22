"""Add subscriber."""

from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication

_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "email": {"type": "string", "description": "Subscriber email."},
    },
    "required": ["email"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "email": "maya@example.com",
    "plan": "free",
    "status": "added",
    "joined_at": "2026-10-11T10:09:00Z",
}


@tool(
    name="add_subscriber",
    title="Add subscriber",
    access="write",
    confirm=True,
    description="Add one email to your list as a free subscriber.",
    details=(
        "Adds one email as a free subscriber, the same as Add subscribers in the dashboard, and Substack sends "
        "its usual welcome email. Substack adds the email in the background, so list_subscribers may show it "
        "a minute later. Add only people who agreed to hear from you. By default you confirm each call; you "
        "can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="POST /subscribers",
    example_response=EXAMPLE_RESPONSE,
)
async def add_subscriber(ctx: ToolContext, args: dict[str, Any]) -> Any:

    email = args["email"].strip().lower()
    if not _EMAIL.match(email):
        raise ToolError("email must be one email address.", ErrorCode.INVALID_INPUT)
    pub = await publication(ctx)
    # The dashboard's "Add subscribers by email" with the welcome email on; Substack adds the email in the background.
    body = {"email": email, "subscription": False, "sendEmail": True}
    await call(ctx, "POST", f"{pub['base']}/api/v1/subscriber/add", body=body)
    return {"email": email, "plan": "free", "status": "added", "joined_at": datetime.now(UTC).isoformat()}
