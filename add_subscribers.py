#!/usr/bin/env python3
"""Add emails from a CSV file (or the command line) to your Substack as free subscribers, or give them a complimentary paid plan.

    python add_subscribers.py --csv workshop.csv --dry-run
    python add_subscribers.py --csv workshop.csv
    python add_subscribers.py --email maya@example.com --plan comp --comp-until 2026-12-31

The CSV needs an "email" column. Substack sends each new subscriber its usual
welcome email. Add only people who agreed to hear from you.
"""
import argparse
import csv

from cotlet_client import call, paginate, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--csv", help="CSV file with an email column")
    parser.add_argument("--email", action="append", default=[], help="Email to add (repeatable)")
    parser.add_argument("--plan", choices=["free", "comp"], default="free")
    parser.add_argument("--comp-until", help="End of the complimentary plan (YYYY-MM-DD), with --plan comp")
    parser.add_argument("--dry-run", action="store_true", help="Only show who would be added")
    args = parser.parse_args()

    emails = list(args.email)
    if args.csv:
        with open(args.csv, newline="", encoding="utf-8-sig") as fh:
            emails += [row["email"].strip() for row in csv.DictReader(fh) if row.get("email", "").strip()]
    if not emails:
        parser.error("pass --csv FILE or --email ADDRESS")

    existing = {s["email"].lower() for s in paginate("list_subscribers", {"limit": 500}, "subscribers")}
    new = sorted({e.lower() for e in emails} - existing)
    print(f"{len(emails)} emails, {len(emails) - len(new)} already subscribed, {len(new)} to add")
    for email in new:
        if args.dry_run:
            print(f"  would add {email} ({args.plan})")
            continue
        result = call("add_subscriber", {"email": email, "plan": args.plan, "comp_until": args.comp_until})
        print(f"  {email}: {result.get('status')}")


if __name__ == "__main__":
    run(main)
