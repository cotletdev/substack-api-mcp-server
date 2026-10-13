#!/usr/bin/env python3
"""Schedule a Substack post for a set time, on the web and by email, from a draft or straight from a Markdown file.

    python schedule_post.py --post-id 148420031 --at 2026-10-14T08:00:00-04:00
    python schedule_post.py --file essay.md --at 2026-10-14T08:00:00-04:00 --note "New essay: why we stopped shipping on Fridays"
    python schedule_post.py --post-id 148420031 --at 2026-10-17T07:00:00+01:00 --web-only

Always give the time with its offset. Substack schedules at most three months
ahead and emails a post only once. The script stops if another post is already
scheduled for the same day, unless you pass --allow-same-day.
"""
import argparse
import json
from datetime import datetime, timedelta, timezone

from cotlet_client import call, paginate, read_markdown, run


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    src = parser.add_mutually_exclusive_group(required=True)
    src.add_argument("--post-id", help="Draft ID")
    src.add_argument("--file", help="Create the draft from this Markdown file first")
    parser.add_argument("--at", required=True, help="ISO 8601 time with offset, e.g. 2026-10-14T08:00:00-04:00")
    parser.add_argument("--audience", choices=["everyone", "only_paid", "founding"], default="everyone", help="With --file")
    parser.add_argument("--web-only", action="store_true", help="Publish on the web without emailing subscribers")
    parser.add_argument("--note", help="Also schedule a Note with a link card to the post")
    parser.add_argument("--note-delay", type=float, default=4, help="Hours after the post for the Note. Default: 4")
    parser.add_argument("--allow-same-day", action="store_true")
    args = parser.parse_args()

    at = datetime.fromisoformat(args.at)
    if at.tzinfo is None:
        parser.error("--at needs a time zone offset, e.g. -04:00 or +01:00")
    now = datetime.now(timezone.utc)
    if at <= now:
        parser.error("--at is in the past")
    if at > now + timedelta(days=92):
        parser.error("Substack schedules at most three months ahead")

    if not args.allow_same_day:
        for post in paginate("list_posts", {"status": "scheduled", "limit": 50}, "posts"):
            when = post.get("publish_at") or post.get("published_at")
            if when and datetime.fromisoformat(when.replace("Z", "+00:00")).astimezone(at.tzinfo).date() == at.date():
                parser.exit(1, f"Already scheduled that day: {post['title']} ({post['post_id']}). Use --allow-same-day.\n")

    post_id = args.post_id
    if args.file:
        title, subtitle, body = read_markdown(args.file)
        post_id = call("create_draft", {"title": title, "subtitle": subtitle, "body_markdown": body, "audience": args.audience})["post_id"]

    scheduled = call("schedule_post", {"post_id": post_id, "publish_at": at.isoformat(), "send_email": not args.web_only})
    print(json.dumps(scheduled, indent=2))
    if args.note:
        note_at = (at + timedelta(hours=args.note_delay)).isoformat()
        print(json.dumps(call("publish_note", {"body": args.note, "link_post_id": post_id, "publish_at": note_at}), indent=2))


if __name__ == "__main__":
    run(main)
