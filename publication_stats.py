#!/usr/bin/env python3
"""Total, paid, new and churned Substack subscribers and revenue for the last 7, 30 or 90 days.

    python publication_stats.py --period 7d
"""
import argparse

from cotlet_client import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--period", choices=["7d", "30d", "90d"], default="30d")
    args = parser.parse_args()

    s = call("get_publication_stats", {"period": args.period})
    paid = s.get("subscribers_paid") or 0
    churn = (s["subscribers_churned"] / paid * 100) if paid else 0
    print(f"Substack publication ({s['period']})")
    print(f"Subscribers:  {s['subscribers_total']:,}")
    print(f"Paid:         {paid:,}")
    print(f"New:          +{s['subscribers_new']:,}")
    print(f"Churned:      -{s['subscribers_churned']:,}  ({churn:.1f}% of paid)")
    print(f"Revenue:      ${s.get('revenue_usd', 0):,}")


if __name__ == "__main__":
    run(main)
