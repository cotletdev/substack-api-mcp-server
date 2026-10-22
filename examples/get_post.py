#!/usr/bin/env python3
"""Save one post of your publication as a Markdown file, with its title and subtitle on top.

    python get_post.py --post-id 148213977 --out the-quiet-launch.md

Post IDs come from list_posts.py. Without --out the post is printed as JSON.
"""

import argparse
import json
from pathlib import Path

from substack_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--post-id", required=True)
    parser.add_argument("--out", help="Save the body as Markdown to this file")
    args = parser.parse_args()

    post = call("get_post", {"post_id": args.post_id})
    if not args.out:
        print(json.dumps(post, indent=2, ensure_ascii=False))
        return
    head = f"# {post.get('title') or ''}\n\n"
    if post.get("subtitle"):
        head += f"{post['subtitle']}\n\n"
    Path(args.out).write_text(head + (post.get("body_markdown") or ""), encoding="utf-8")
    print(f"Saved {args.out}")


if __name__ == "__main__":
    run(main)
