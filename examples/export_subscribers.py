#!/usr/bin/env python3
"""Download your full subscriber list as the same CSV that Export gives in the Substack dashboard.

    python export_subscribers.py --out subscribers.csv

Substack builds the file in the background; this waits for it. For filtered lists use list_subscribers.py.
"""

import argparse
import sys
import urllib.request

from substack_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", required=True, help="CSV file to write")
    args = parser.parse_args()

    export = call("export_subscribers")
    with urllib.request.urlopen(export["download_url"], timeout=120) as response, open(args.out, "wb") as fh:
        fh.write(response.read())
    print(f"Saved {export.get('rows')} subscribers to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    run(main)
