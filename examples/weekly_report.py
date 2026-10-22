#!/usr/bin/env python3
"""Last week on your Substack: new and paid subscribers, cancellations, revenue, and each new post's numbers.

    python weekly_report.py
    python weekly_report.py --period 30d --out report.json

Run it from cron on Monday morning and send the output wherever you read reports.
"""

import argparse
import json
from datetime import UTC, datetime, timedelta
from pathlib import Path

from substack_api_mcp.scripting import call, paginate, run

DAYS = {"7d": 7, "30d": 30, "90d": 90}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--period", choices=list(DAYS), default="7d")
    parser.add_argument("--out", help="Save the report as JSON")
    args = parser.parse_args()

    since = datetime.now(UTC) - timedelta(days=DAYS[args.period])
    posts = []
    for post in paginate("list_posts", {"status": "published", "limit": 50}, "posts"):
        published = post.get("published_at")
        if not published or datetime.fromisoformat(published.replace("Z", "+00:00")) < since:
            break
        stats = call("get_post_stats", {"post_id": post["post_id"]})
        posts.append({"title": post["title"], "url": post.get("url"), **stats})
    report = {"publication": call("get_publication_stats", {"period": args.period}), "posts": posts}
    text = json.dumps(report, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Saved {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    run(main)
