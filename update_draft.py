#!/usr/bin/env python3
"""Change the title, subtitle, body or audience of a Substack draft. Published posts are not changed.

    python update_draft.py --post-id 148420031 --file essay.md
    python update_draft.py --post-id 148420031 --title "Notes on pricing, part 2"
"""
import argparse
import json

from cotlet_client import call, read_markdown, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--post-id", required=True, help="Draft ID from create_draft.py or list_posts.py --status draft")
    parser.add_argument("--file", help="Replace title, subtitle and body from this Markdown file")
    parser.add_argument("--title")
    parser.add_argument("--subtitle")
    parser.add_argument("--audience", choices=["everyone", "only_paid", "founding"])
    args = parser.parse_args()

    fields = {}
    if args.file:
        title, subtitle, body = read_markdown(args.file)
        fields.update({"title": title, "subtitle": subtitle, "body_markdown": body})
    fields.update({k: v for k, v in {"title": args.title, "subtitle": args.subtitle, "audience": args.audience}.items() if v})
    fields = {k: v for k, v in fields.items() if v is not None}
    if not fields:
        parser.error("pass --file or at least one of --title, --subtitle, --audience")

    print(json.dumps(call("update_draft", {"post_id": args.post_id, "fields": fields}), indent=2))


if __name__ == "__main__":
    run(main)
