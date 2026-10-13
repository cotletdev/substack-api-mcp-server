#!/usr/bin/env python3
"""Export your Substack subscribers to CSV: email, plan, join date and activity rating.

    python export_subscribers.py --out subscribers.csv
    python export_subscribers.py --plan paid --out paid.csv
    python export_subscribers.py --since 2026-10-01 --out new-this-month.json

Without filters you get Substack's own full export (the same CSV as Export in
the subscriber dashboard). With --plan or --since the list is paged through
list_subscribers instead.
"""
import argparse
import sys
import urllib.request

from cotlet_client import USER_AGENT, call, paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", choices=["all", "free", "paid", "comp", "founding"], default="all")
    parser.add_argument("--since", help="Only subscribers who joined on or after this date (YYYY-MM-DD)")
    parser.add_argument("--max", type=int, help="Stop after this many subscribers")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    if args.plan == "all" and not args.since and not args.max and args.out and args.out.lower().endswith(".csv"):
        export = call("export_subscribers")
        req = urllib.request.Request(export["download_url"], headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=300) as resp, open(args.out, "wb") as fh:
            fh.write(resp.read())
        print(f"Saved {export['rows']} subscribers to {args.out}", file=sys.stderr)
        return

    params = {"plan": args.plan, "since": args.since, "limit": 500}
    write_rows(list(paginate("list_subscribers", params, "subscribers", args.max)), args.out)


if __name__ == "__main__":
    run(main)
