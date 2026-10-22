#!/usr/bin/env python3
"""Add emails from a file to your list as free subscribers, one call per email.

    python add_subscribers.py emails.txt
    python add_subscribers.py contacts.csv --column email --yes

Each address gets Substack's welcome email. Add only people who asked to subscribe.
"""

import argparse
import csv
import sys
from pathlib import Path

from substack_api_mcp.core.errors import ToolError
from substack_api_mcp.scripting import call, run


def read_emails(path: Path, column: str | None) -> list[str]:
    if column:
        with path.open(newline="", encoding="utf-8") as fh:
            return [row[column].strip() for row in csv.DictReader(fh) if row.get(column, "").strip()]
    return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if "@" in line]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", help="Text file with one email per line, or a CSV with --column")
    parser.add_argument("--column", help="CSV column that holds the email")
    parser.add_argument("--yes", action="store_true", help="Do not ask before adding")
    args = parser.parse_args()

    emails = list(dict.fromkeys(read_emails(Path(args.file), args.column)))
    if not args.yes and input(f"Add {len(emails)} emails as free subscribers? [y/N] ").lower() != "y":
        sys.exit("Nothing added.")
    for email in emails:
        try:
            call("add_subscriber", {"email": email})
            print(f"added   {email}")
        except ToolError as err:
            print(f"skipped {email}: {err}", file=sys.stderr)


if __name__ == "__main__":
    run(main)
