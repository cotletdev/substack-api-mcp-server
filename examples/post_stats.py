#!/usr/bin/env python3
"""Opens, open rate, views, likes, restacks and new subscribers for your recent posts, one row per post.

python post_stats.py --last 10 --out post-stats.csv
"""

import argparse

from substack_api_mcp.scripting import call, paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--last", type=int, default=10, help="How many recent published posts (default 10)")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    rows = []
    for post in paginate("list_posts", {"status": "published", "limit": 50}, "posts", args.last):
        stats = call("get_post_stats", {"post_id": post["post_id"]})
        rows.append({"title": post["title"], "published_at": post.get("published_at"), **stats})
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
