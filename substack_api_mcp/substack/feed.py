"""Items of Substack's reader feeds (search, home feed): posts and Notes in one shape for our answers."""

from __future__ import annotations

from typing import Any

from substack_api_mcp.substack.client import person


def post_item(item: dict[str, Any]) -> dict[str, Any]:
    post, pub = item["post"], item.get("publication") or {}
    return {
        "post_id": str(post["id"]),
        "title": post.get("title") or "",
        "publication": pub.get("name") or "",
        "publication_id": str(post.get("publication_id") or pub.get("id") or ""),
        "published_at": post.get("post_date"),
        "likes": int(post.get("reaction_count") or 0),
        "url": post.get("canonical_url"),
    }


def note_item(item: dict[str, Any]) -> dict[str, Any]:
    note = item["comment"]
    return {
        "note_id": str(note["id"]),
        "author": person({"id": note.get("user_id"), "name": note.get("name"), "handle": note.get("handle")}),
        "body": note.get("body") or "",
        "published_at": note.get("date"),
        "likes": int(note.get("reaction_count") or 0),
    }
