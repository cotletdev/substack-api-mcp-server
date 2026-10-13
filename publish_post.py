#!/usr/bin/env python3
"""Publish a Substack draft now, on the web and by email unless you pass --web-only.

    python publish_post.py --post-id 148420031
    python publish_post.py --post-id 148420031 --web-only

A sent email cannot be recalled. By default Cotlet asks you to confirm first.
"""
import argparse
import json

from cotlet_client import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--post-id", required=True, help="Draft ID")
    parser.add_argument("--web-only", action="store_true", help="Publish on the web without emailing subscribers")
    args = parser.parse_args()

    print(json.dumps(call("publish_post", {"post_id": args.post_id, "send_email": not args.web_only}), indent=2))


if __name__ == "__main__":
    run(main)
