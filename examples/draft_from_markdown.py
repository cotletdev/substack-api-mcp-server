#!/usr/bin/env python3
"""Turn a Markdown file into a Substack draft, and schedule it if you give a time.

    python draft_from_markdown.py essay.md
    python draft_from_markdown.py essay.md --audience only_paid --publish-at 2026-11-03T08:00:00-05:00

The first "# " heading is the title and the line right after it, if it is not empty, the subtitle.
Images must be public URLs. Without --publish-at the draft only waits in Substack for you.
"""

import argparse
import json
from pathlib import Path

from substack_api_mcp.scripting import call, run


def split(text: str) -> tuple[str, str | None, str]:
    lines = text.strip().splitlines()
    if not lines or not lines[0].startswith("# "):
        raise SystemExit('The file must start with a "# Title" line.')
    title = lines[0][2:].strip()
    rest = lines[1:]
    subtitle = None
    if rest and rest[0].strip() and not rest[0].startswith("#"):
        subtitle, rest = rest[0].strip(), rest[1:]
    return title, subtitle, "\n".join(rest).strip()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file", help="Markdown file")
    parser.add_argument("--audience", choices=["everyone", "only_paid", "founding"], default="everyone")
    parser.add_argument("--publish-at", help="ISO time with an offset, e.g. 2026-11-03T08:00:00-05:00")
    parser.add_argument("--no-email", action="store_true", help="Publish on the web only, send no email")
    args = parser.parse_args()

    title, subtitle, body = split(Path(args.file).read_text(encoding="utf-8"))
    draft = call(
        "create_draft", {"title": title, "subtitle": subtitle, "body_markdown": body, "audience": args.audience}
    )
    print(json.dumps(draft, indent=2))
    if args.publish_at:
        params = {"post_id": draft["post_id"], "publish_at": args.publish_at, "send_email": not args.no_email}
        print(json.dumps(call("schedule_post", params), indent=2))


if __name__ == "__main__":
    run(main)
