#!/usr/bin/env python3
"""Reply as you under a comment on one of your posts.

    python reply_to_comment.py --comment-id 98765432 --body "Thanks, glad it helped."

Comment IDs come from unanswered_comments.py. The reply is public and the commenter is notified.
"""

import argparse
import json

from substack_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--comment-id", required=True)
    parser.add_argument("--body", required=True, help="Reply text")
    args = parser.parse_args()

    print(json.dumps(call("reply_to_comment", {"comment_id": args.comment_id, "body": args.body}), indent=2))


if __name__ == "__main__":
    run(main)
