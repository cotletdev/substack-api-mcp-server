#!/usr/bin/env python3
"""Comments on your recent Substack posts that you have not answered yet.

    python unanswered_comments.py --last 3
    python unanswered_comments.py --days 14 --out unanswered.csv

Reply with reply_to_comment.py, or let your AI agent draft the replies over MCP.
"""
import argparse
from datetime import date, timedelta

from cotlet_client import call, paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    window = parser.add_mutually_exclusive_group()
    window.add_argument("--last", type=int, default=3, help="Check the last N published posts. Default: 3")
    window.add_argument("--days", type=int, help="Check every post published in the last N days")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    since = (date.today() - timedelta(days=args.days)).isoformat() if args.days else None
    rows = []
    checked = 0
    for post in paginate("list_posts", {"status": "published", "limit": 50}, "posts"):
        if since and post["published_at"][:10] < since:
            break
        if not since and checked >= args.last:
            break
        checked += 1
        for c in call("list_comments", {"post_id": post["post_id"], "unanswered_only": True}).get("comments", []):
            rows.append({"post": post["title"], "comment_id": c["comment_id"], "author": c["author"],
                         "body": c["body"], "created_at": c["created_at"], "post_url": post.get("url")})
    print(f"Checked {checked} posts, {len(rows)} comments waiting for you")
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
