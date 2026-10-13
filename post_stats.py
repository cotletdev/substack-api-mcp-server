#!/usr/bin/env python3
"""Opens, open rate, views, likes, restacks and new subscribers for your recent Substack posts, in one table.

    python post_stats.py --last 10
    python post_stats.py --since 2026-09-01 --out post-stats.csv
    python post_stats.py --post-id 148213977

Numbers keep growing for days after a send, so a post sent yesterday is marked as early.
"""
import argparse
from datetime import datetime, timedelta, timezone

from cotlet_client import call, paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--post-id", help="Only this post")
    parser.add_argument("--last", type=int, default=10, help="Number of recent published posts. Default: 10")
    parser.add_argument("--since", help="Only posts published on or after this date (YYYY-MM-DD)")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    if args.post_id:
        posts = [call("get_post", {"post_id": args.post_id})]
    else:
        posts = []
        for post in paginate("list_posts", {"status": "published", "limit": 50}, "posts"):
            if args.since and post["published_at"][:10] < args.since:
                break
            posts.append(post)
            if not args.since and len(posts) >= args.last:
                break

    early = datetime.now(timezone.utc) - timedelta(days=2)
    rows = []
    for post in posts:
        stats = call("get_post_stats", {"post_id": post["post_id"]})
        published = post.get("published_at")
        rows.append({
            "title": post["title"],
            "published_at": published,
            **{k: v for k, v in stats.items() if k != "post_id"},
            "early": bool(published) and datetime.fromisoformat(published.replace("Z", "+00:00")) > early,
            "url": post.get("url"),
        })
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
