#!/usr/bin/env python3
"""Comments on your recent posts that you have not replied to yet, so you (or your agent) can answer.

    python unanswered_comments.py --last 3
    python unanswered_comments.py --last 10 --out todo.csv

Reply with reply_to_comment.py and the comment_id from the output.
"""

import argparse

from substack_api_mcp.scripting import call, paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--last", type=int, default=3, help="How many recent published posts (default 3)")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    rows = []
    for post in paginate("list_posts", {"status": "published", "limit": 50}, "posts", args.last):
        comments = call("list_comments", {"post_id": post["post_id"], "unanswered_only": True})["comments"]
        for comment in comments:
            rows.append(
                {
                    "post": post["title"],
                    "comment_id": comment["comment_id"],
                    "author": comment["author"],
                    "body": comment["body"],
                    "created_at": comment.get("created_at"),
                }
            )
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
