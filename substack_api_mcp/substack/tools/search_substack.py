"""Search Substack."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from substack_api_mcp.core.errors import ErrorCode, ToolError
from substack_api_mcp.core.tools import tool
from substack_api_mcp.substack.client import WEB, call, person
from substack_api_mcp.substack.feed import note_item, post_item

if TYPE_CHECKING:
    from substack_api_mcp.core.context import ToolContext

INPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "query": {"type": "string", "description": "Words to search for."},
        "cursor": {"type": "string", "description": "next_cursor from the previous page."},
    },
    "required": ["query"],
    "additionalProperties": False,
}

EXAMPLE_RESPONSE: dict[str, Any] = {
    "people": [{"user_id": "528339521", "name": "Routine Morning", "handle": "routinemorning", "bio": "Small habits."}],
    "posts": [
        {
            "post_id": "197396217",
            "title": "A Guide to Your Morning Routine",
            "publication": "Brain Health Decoded",
            "publication_id": "5262902",
            "published_at": "2026-05-12T19:25:47.700Z",
            "likes": 410,
            "url": "https://example.substack.com/p/a-guide-to-your-morning-routine",
        }
    ],
    "notes": [
        {
            "note_id": "322981144",
            "author": {"user_id": "18270011", "name": "Laura Mills", "handle": "lauramills"},
            "body": "Morning light beats any supplement.",
            "published_at": "2026-09-02T07:11:00.000Z",
            "likes": 88,
        }
    ],
    "next_cursor": "eyJvZmZzZXQiOjIwfQ==",
}


@tool(
    name="search_substack",
    title="Search Substack",
    access="read",
    confirm=False,
    description="Search all of Substack for people, posts and Notes.",
    details=(
        "Runs Substack's search as the search box does and splits the results into people, posts and Notes. "
        "Use the IDs with follow_user, like_post, like_comment, reply_to_note, send_message or "
        "recommend_publication. Page with next_cursor; later pages may hold only posts and Notes."
    ),
    input_schema=INPUT_SCHEMA,
    route="GET /search",
    example_response=EXAMPLE_RESPONSE,
)
async def search_substack(ctx: ToolContext, args: dict[str, Any]) -> Any:

    query = str(args["query"]).strip()
    if not query:
        raise ToolError("query must not be empty.", ErrorCode.INVALID_INPUT)
    params = {"query": query, **({"cursor": args["cursor"]} if args.get("cursor") else {})}
    answer = await call(ctx, "GET", f"{WEB}/api/v1/top/search", params=params)
    people: list[dict[str, Any]] = []
    posts: list[dict[str, Any]] = []
    notes: list[dict[str, Any]] = []
    for item in answer.get("items") or []:
        kind = item.get("type")
        if kind == "profileSearchResults":
            people += [{**person(row), "bio": row.get("bio") or ""} for row in item.get("results") or []]
        elif kind == "post" and item.get("post"):
            posts.append(post_item(item))
        elif kind == "comment" and item.get("comment"):
            notes.append(note_item(item))
    return {"people": people, "posts": posts, "notes": notes, "next_cursor": answer.get("nextCursor")}
