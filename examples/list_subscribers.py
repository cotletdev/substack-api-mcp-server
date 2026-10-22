#!/usr/bin/env python3
"""Subscribers by plan or join date, with activity rating, to CSV or JSON.

python list_subscribers.py --plan paid --out paid.csv
python list_subscribers.py --since 2026-10-01 --out new-this-month.csv
"""

import argparse

from substack_api_mcp.scripting import paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", choices=["all", "free", "paid", "comp", "founding"], default="all")
    parser.add_argument("--since", help="Only subscribers who joined on or after this date (YYYY-MM-DD)")
    parser.add_argument("--max", type=int, help="Stop after this many subscribers")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    params = {"plan": args.plan, "since": args.since, "limit": 500}
    write_rows(list(paginate("list_subscribers", params, "subscribers", args.max)), args.out)


if __name__ == "__main__":
    run(main)
