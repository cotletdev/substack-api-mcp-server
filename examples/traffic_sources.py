#!/usr/bin/env python3
"""Where your publication's visitors came from in a period, most views first.

python traffic_sources.py --period 30d --out sources.csv
"""

import argparse

from substack_api_mcp.scripting import paginate, run, write_rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--period", choices=["7d", "30d", "90d", "365d"], default="30d")
    parser.add_argument("--out", help="Save to .csv or .json instead of printing")
    args = parser.parse_args()

    rows = list(paginate("list_traffic_sources", {"period": args.period, "limit": 50}, "sources"))
    write_rows(rows, args.out)


if __name__ == "__main__":
    run(main)
