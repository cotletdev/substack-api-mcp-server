#!/usr/bin/env python3
"""Export your Substack posts as Markdown files, one per post, including the paywalled part of your own posts.

    python export_posts.py --dir posts
    python export_posts.py --dir posts --since 2026-01-01
    python export_posts.py --dir drafts --status draft

Each file is named after the post URL slug and starts with the title and subtitle.
Images stay as URLs. Works for the publication your Substack account publishes to.
"""
import argparse
import re
import sys
from pathlib import Path

from cotlet_client import call, paginate, run


def slug(post: dict) -> str:
    source = (post.get("url") or "").rstrip("/").rsplit("/", 1)[-1] or post.get("title") or post["post_id"]
    return re.sub(r"[^a-z0-9]+", "-", source.lower()).strip("-") or post["post_id"]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dir", required=True, help="Folder to write the .md files to")
    parser.add_argument("--status", choices=["published", "draft", "scheduled"], default="published")
    parser.add_argument("--since", help="Only posts published on or after this date (YYYY-MM-DD)")
    parser.add_argument("--max", type=int, help="Stop after this many posts")
    args = parser.parse_args()

    out = Path(args.dir)
    out.mkdir(parents=True, exist_ok=True)
    count = 0
    for item in paginate("list_posts", {"status": args.status, "limit": 50}, "posts", args.max):
        if args.since and item.get("published_at") and item["published_at"][:10] < args.since:
            break  # newest first: everything after this is older
        post = call("get_post", {"post_id": item["post_id"]})
        head = f"# {post['title']}\n\n" + (f"_{post['subtitle']}_\n\n" if post.get("subtitle") else "")
        path = out / f"{slug(post)}.md"
        path.write_text(head + post.get("body_markdown", "") + "\n", encoding="utf-8")
        print(f"  {path}", file=sys.stderr)
        count += 1
    print(f"Exported {count} posts to {out}", file=sys.stderr)


if __name__ == "__main__":
    run(main)
