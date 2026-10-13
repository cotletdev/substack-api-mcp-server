#!/usr/bin/env python3
"""Turn a Markdown file into a Substack draft, keeping headings, bold, links and lists.

    python create_draft.py --file essay.md
    python create_draft.py --file essay.md --audience only_paid

The first "# " heading becomes the title and a "## " or _italic_ line right
under it the subtitle. Images must be URLs; local paths are reported, not
uploaded. Nothing is sent: schedule it with schedule_post.py or open the edit link.
"""
import argparse
import json
import re
import sys

from cotlet_client import call, read_markdown, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--file", required=True, help="Markdown file")
    parser.add_argument("--title", help="Override the title taken from the file")
    parser.add_argument("--subtitle", help="Override the subtitle taken from the file")
    parser.add_argument("--audience", choices=["everyone", "only_paid", "founding"], default="everyone")
    args = parser.parse_args()

    title, subtitle, body = read_markdown(args.file)
    local = [src for src in re.findall(r"!\[[^\]]*\]\(([^)\s]+)", body) if not src.startswith(("http://", "https://"))]
    for src in local:
        print(f"Warning: image {src} is a local path; replace it with a hosted URL", file=sys.stderr)

    draft = call("create_draft", {
        "title": args.title or title,
        "subtitle": args.subtitle or subtitle,
        "body_markdown": body,
        "audience": args.audience,
    })
    print(json.dumps(draft, indent=2))


if __name__ == "__main__":
    run(main)
