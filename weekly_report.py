#!/usr/bin/env python3
"""Weekly Substack report: new, paid and churned subscribers, revenue, and how each post of the week did.

    python weekly_report.py
    python weekly_report.py --save last-week.json

With --save the totals are stored, and the next run with the same file adds a
week-on-week line. Revenue is Substack's gross annualized figure, not cash received.
"""
import argparse
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cotlet_client import call, paginate, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--save", help="JSON file to compare with and update, e.g. last-week.json")
    args = parser.parse_args()

    week = call("get_publication_stats", {"period": "7d"})
    month = call("get_publication_stats", {"period": "30d"})
    weekly_churn = month["subscribers_churned"] / 30 * 7

    print(f"Subscribers: {week['subscribers_total']:,} total (+{week['subscribers_new']} new)")
    flag = "  (flagged: above the 30-day weekly average)" if week["subscribers_churned"] > weekly_churn else ""
    print(f"Paid: {week['subscribers_paid']:,}, churned {week['subscribers_churned']} "
          f"(30-day weekly average: {weekly_churn:.0f}){flag}")
    print(f"Gross annualized revenue: ${week.get('revenue_usd', 0):,}")

    now = datetime.now(timezone.utc)
    print("Posts this week:")
    for post in paginate("list_posts", {"status": "published", "limit": 50}, "posts"):
        published = datetime.fromisoformat(post["published_at"].replace("Z", "+00:00"))
        if published < now - timedelta(days=7):
            break
        s = call("get_post_stats", {"post_id": post["post_id"]})
        early = " (early, under 2 days of data)" if published > now - timedelta(days=2) else ""
        print(f'  "{post["title"]}": open rate {s["open_rate"]:.1%}, {s["subscribers_gained"]} new subscribers{early}')

    if args.save:
        path = Path(args.save)
        if path.exists():
            prev = json.loads(path.read_text())
            print(f"Week on week: total {week['subscribers_total'] - prev['subscribers_total']:+,}, "
                  f"paid {week['subscribers_paid'] - prev['subscribers_paid']:+,}")
        else:
            print("Week on week: no stored copy yet, saved this week for next time")
        path.write_text(json.dumps(week, indent=2))


if __name__ == "__main__":
    run(main)
