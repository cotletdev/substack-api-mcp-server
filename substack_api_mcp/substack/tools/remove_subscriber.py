"""Remove subscriber."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import call, publication
from substack_api_mcp.substack.subscribers import find_subscriber

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {"email": {"type": "string", "description": "Subscriber's email address."}},
    "required": ["email"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {"email": "reader@example.com", "removed": True}


@tool(
    name="remove_subscriber",
    title="Remove subscriber",
    access="write",
    confirm=True,
    description="Remove one email from your subscriber list.",
    details=(
        "Removes a subscriber from your list, as Remove in the subscriber's menu does: they get no more emails "
        "from you and no notice. A paid subscription is cancelled and Substack refunds the unused part. An "
        "email not on your list returns an error; add_subscriber takes about a minute before the address is "
        "listed. By default you confirm each call; you can switch that off for this tool."
    ),
    input_schema=INPUT_SCHEMA,
    route="DELETE /subscribers/{email}",
    example_response=EXAMPLE_RESPONSE,
)
async def remove_subscriber(ctx: ToolContext, args: dict[str, Any]) -> Any:

    email = str(args["email"]).strip()
    if not re.fullmatch(r"[^@\s/]+@[^@\s/]+\.[^@\s/]+", email):
        raise ToolError("email must be one email address.", ErrorCode.INVALID_INPUT)
    pub = await publication(ctx)
    row = await find_subscriber(ctx, pub, email)
    if not row:
        # Substack answers 200 to a removal of an address it does not have, so the table decides.
        raise ToolError(
            "This email is not on your subscriber list. One added in the last few minutes may not be listed "
            "yet; try again shortly.",
            ErrorCode.TARGET_ERROR,
        )
    await call(ctx, "DELETE", f"{pub['base']}/api/v1/subscriber-stats/remove/{row['user_email_address']}")
    return {"email": row["user_email_address"], "removed": True}
