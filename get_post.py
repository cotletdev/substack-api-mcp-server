#!/usr/bin/env python3
"""Get one Substack post with its full body as Markdown, audience, URL and dates.

    python get_post.py --post-id 148213977
    python get_post.py --post-id 148213977 --markdown > the-quiet-launch.md
"""
import argparse
import json

from cotlet_client import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--post-id", required=True, help="Post ID from list_posts.py")
    parser.add_argument("--markdown", action="store_true", help="Print only the post as Markdown")
    args = parser.parse_args()

    post = call("get_post", {"post_id": args.post_id})
    if args.markdown:
        print(f"# {post['title']}\n")
        if post.get("subtitle"):
            print(f"_{post['subtitle']}_\n")
        print(post.get("body_markdown", ""))
    else:
        print(json.dumps(post, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    run(main)
