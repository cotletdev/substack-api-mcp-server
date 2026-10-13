#!/usr/bin/env python3
"""List the posts of your Substack publication: published, drafts or scheduled, newest first.

    python list_posts.py
    python list_posts.py --status scheduled
    python list_posts.py --status draft --out drafts.csv

Scheduled posts include their publish time. Pages are followed automatically.
"""
import argparse

from cotlet_client import paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--status", choices=["published", "draft", "scheduled"], default="published")
    parser.add_argument("--max", type=int, help="Stop after this many posts")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    rows = list(paginate("list_posts", {"status": args.status, "limit": 50}, "posts", args.max))
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
