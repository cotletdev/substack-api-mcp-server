#!/usr/bin/env python3
"""Post a Substack Note now or at a set time, optionally with a link card to one of your posts.

    python publish_note.py --body "New essay is out."  --link-latest
    python publish_note.py --body-file note.txt --publish-at 2026-11-03T09:00:00-05:00

A link card needs a published post. --link-latest takes your newest published post.
"""

import argparse
import json
from pathlib import Path

from substack_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    body = parser.add_mutually_exclusive_group(required=True)
    body.add_argument("--body", help="Note text")
    body.add_argument("--body-file", help="Read the Note text from a file")
    link = parser.add_mutually_exclusive_group()
    link.add_argument("--link-post-id", help="Published post to show as a link card")
    link.add_argument("--link-latest", action="store_true", help="Link your newest published post")
    parser.add_argument("--publish-at", help="ISO time with an offset; now when left out")
    args = parser.parse_args()

    text = args.body if args.body is not None else Path(args.body_file).read_text(encoding="utf-8").strip()
    post_id = args.link_post_id
    if args.link_latest:
        posts = call("list_posts", {"status": "published", "limit": 1})["posts"]
        if not posts:
            raise SystemExit("No published post to link.")
        post_id = posts[0]["post_id"]
    result = call("publish_note", {"body": text, "link_post_id": post_id, "publish_at": args.publish_at})
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run(main)
