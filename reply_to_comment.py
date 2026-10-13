#!/usr/bin/env python3
"""Reply as you under a comment on one of your Substack posts.

    python reply_to_comment.py --comment-id c_90417 --body "Thank you, Maya. Pricing is the whole of part two."

The commenter gets Substack's usual reply notification. By default Cotlet asks you to confirm first.
"""
import argparse
import json

from cotlet_client import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--comment-id", required=True, help="Comment ID from unanswered_comments.py")
    parser.add_argument("--body", required=True, help="Reply text")
    args = parser.parse_args()

    print(json.dumps(call("reply_to_comment", {"comment_id": args.comment_id, "body": args.body}), indent=2))


if __name__ == "__main__":
    run(main)
