#!/usr/bin/env python3
"""Post a Substack Note now or at a set time, optionally with a link card to one of your posts.

    python publish_note.py --body "Tuesday's essay is out." --link-latest
    python publish_note.py --body "Part two is coming." --link-post-id 148213977 --at 2026-10-14T12:00:00-04:00

Notes are up to 1,000 characters and are not emailed to subscribers.
"""
import argparse
import json

from cotlet_client import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--body", required=True, help="Note text, up to 1,000 characters")
    link = parser.add_mutually_exclusive_group()
    link.add_argument("--link-post-id", help="Attach this post as a card")
    link.add_argument("--link-latest", action="store_true", help="Attach your latest published post")
    parser.add_argument("--at", help="ISO 8601 time with offset. Omit to post now")
    args = parser.parse_args()
    if len(args.body) > 1000:
        parser.error(f"Note is {len(args.body)} characters, the limit is 1,000")

    post_id = args.link_post_id
    if args.link_latest:
        posts = call("list_posts", {"status": "published", "limit": 1}).get("posts", [])
        post_id = posts[0]["post_id"] if posts else None

    print(json.dumps(call("publish_note", {"body": args.body, "link_post_id": post_id, "publish_at": args.at}), indent=2))


if __name__ == "__main__":
    run(main)
