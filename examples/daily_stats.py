#!/usr/bin/env python3
"""Day by day: total and paid subscribers, followers and views, to CSV or JSON.

python daily_stats.py --period 90d --out daily.csv
"""

import argparse

from substack_api_mcp.scripting import call, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--period", choices=["7d", "30d", "90d", "365d"], default="30d")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    write_rows(call("get_daily_stats", {"period": args.period})["days"], args.out)


if __name__ == "__main__":
    run(main)
