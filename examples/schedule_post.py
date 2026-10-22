#!/usr/bin/env python3
"""Schedule a draft to go out at a set time, on the web and by email, or cancel a scheduled post.

    python schedule_post.py --post-id 148420031 --publish-at 2026-11-03T08:00:00-05:00
    python schedule_post.py --post-id 148420031 --cancel

The time needs an explicit offset and must be in the future. Cancelling keeps the post as a draft.
"""

import argparse
import json

from substack_api_mcp.scripting import call, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--post-id", required=True, help="Draft ID from list_posts.py --status draft")
    when = parser.add_mutually_exclusive_group(required=True)
    when.add_argument("--publish-at", help="ISO time with an offset")
    when.add_argument("--cancel", action="store_true", help="Cancel the schedule")
    parser.add_argument("--no-email", action="store_true", help="Publish on the web only, send no email")
    args = parser.parse_args()

    if args.cancel:
        result = call("cancel_scheduled_post", {"post_id": args.post_id})
    else:
        params = {"post_id": args.post_id, "publish_at": args.publish_at, "send_email": not args.no_email}
        result = call("schedule_post", params)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    run(main)
