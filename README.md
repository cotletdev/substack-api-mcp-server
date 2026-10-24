# Substack API and MCP server, self-hosted

A **Substack API** and a **Substack MCP server** you run on your own computer, in Python, on the session of your own Google Chrome. All 50 Substack tools we run in production at [Cotlet](https://cotlet.dev/integrations/substack-api-mcp-server): posts and drafts from Markdown, publishing and scheduling, Notes, comments, subscribers, stats, recommendations and direct messages.

Substack has no public API to write posts, publish Notes or manage subscribers, and no official MCP server. This repo gives you both:

- **MCP server** for Claude Code, Claude Desktop, Cursor, Codex and any MCP client, over stdio or HTTP. [Setup](#mcp-server)
- **REST API** on `http://127.0.0.1:8787/api/v1/substack`, with OpenAPI docs at `/docs`. [Setup](#rest-api)
- **Python**: `call("list_posts", status="draft")`, plus 14 ready scripts in [`examples/`](examples/).

It is for technical people who want to run it themselves, **for noncommercial use only** ([license](#license)). If you want it running 24/7 on a server, kept working when Substack changes its site, for a team or a business, use the [hosted version at cotlet.dev](https://cotlet.dev/integrations/substack-api-mcp-server).

[![Substack MCP server](https://img.shields.io/badge/Substack%20MCP-50%20tools-ff6719)](#all-50-tools)
[![Python 3.11+](https://img.shields.io/badge/python-3.11%2B-141318)](#requirements)
[![License: PolyForm Noncommercial 1.0.0](https://img.shields.io/badge/license-PolyForm%20Noncommercial-141318)](LICENSE)
[![MCP Badge](https://lobehub.com/badge/mcp/cotletdev-substack-api-mcp-server)](https://lobehub.com/mcp/cotletdev-substack-api-mcp-server)

```bash
uv tool install substack-api-mcp                  # or: pip install substack-api-mcp
substack-mcp connect                               # reads your Substack session from Chrome
substack-mcp call list_posts
claude mcp add substack -- uvx --from substack-api-mcp substack-mcp mcp
```

## Contents

- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Install](#install)
- [Connect your Chrome](#connect-your-chrome)
- [MCP server](#mcp-server)
- [REST API](#rest-api)
- [Python and the example scripts](#python-and-the-example-scripts)
- [All 50 tools](#all-50-tools)
- [Configuration](#configuration)
- [Security and your Substack account](#security-and-your-substack-account)
- [Errors](#errors)
- [Self-hosted or hosted](#self-hosted-or-hosted)
- [FAQ](#faq)
- [License](#license)

## How it works

```text
AI agent (MCP) / script (REST, Python) ──▶ substack-mcp on your computer ──your Substack cookies──▶ substack.com
                                                     ▲
                         substack-mcp connect ───────┘ reads them once from your Chrome (DevTools Protocol)
```

1. You sign in to Substack in your own Chrome, the way you always do.
2. `substack-mcp connect` attaches to that Chrome through the Chrome DevTools Protocol, reads the substack.com cookies and saves them to `~/.config/substack-api-mcp/session.json`, readable by your user only. Substack signs in by an emailed code or link, so there is no password to see or store.
3. Every tool call is a request to Substack's own web app endpoints (`substack.com/api/v1` for the reader side, `yourname.substack.com/api/v1` for your publication's dashboard) with those cookies, sent with [curl_cffi](https://github.com/lexiforest/curl_cffi), which copies Chrome's TLS fingerprint. No headless browser runs.

Substack's session cookie (`substack.sid`) lasts about three months. When Substack signs you out, the server reads the cookies from Chrome again, if Chrome is open with remote debugging on.

## Requirements

- Python 3.11 or newer.
- Google Chrome 144 or newer, signed in to Substack. Any Chrome or Chromium works with a [debugging port](#option-b-a-chrome-with-a-debugging-port).
- macOS, Linux or Windows.
- A Substack account. Publisher tools (posts, subscribers, stats, comments) work on the first publication your account runs as admin, owner, editor or contributor. Reader tools (feed, search, Notes, messages) work on any account.

## Install

From [PyPI](https://pypi.org/project/substack-api-mcp/):

```bash
uv tool install substack-api-mcp       # or: pipx install substack-api-mcp, or: pip install substack-api-mcp
substack-mcp --version
```

MCP clients can also run it with no install: `uvx --from substack-api-mcp substack-mcp mcp`.

From source:

```bash
git clone https://github.com/cotletdev/substack-api-mcp-server.git
cd substack-api-mcp-server
python3 -m venv .venv
. .venv/bin/activate              # Windows: .venv\Scripts\activate
pip install -e .
substack-mcp --version
```

With [uv](https://docs.astral.sh/uv/): `uv venv && uv pip install -e .`, then `uv run substack-mcp ...`.

Setting it up with an AI agent (Claude Code, Codex, Cursor)? Open it in this folder and ask it to set up the repo: [`AGENTS.md`](AGENTS.md) tells it every step, and it asks you only for the steps in Chrome.

To update: `uv tool upgrade substack-api-mcp` (or `pip install -U substack-api-mcp`), from source `git pull && pip install -e .`. We copy every change of the hosted Substack tools into this repo.

## Connect your Chrome

### Option A: your everyday Chrome (recommended)

1. Open `chrome://inspect/#remote-debugging` in Chrome and switch **remote debugging** on. Chrome then accepts DevTools connections from programs on this computer, and asks you before each one.
2. Make sure you are signed in at [substack.com](https://substack.com).
3. Run:

   ```bash
   substack-mcp connect
   ```

4. Chrome asks whether to allow the connection. Click **Allow**.

```text
Saved 19 Substack cookies to /Users/you/.config/substack-api-mcp/session.json
Signed in to Substack as Maya Chen (@mayachen)
```

You can switch remote debugging off again afterwards. Leave it on if you want the server to pick up a new session by itself after Substack signs you out.

`connect` looks for Chrome's `DevToolsActivePort` file in the default profile folder. For Chrome Beta, Canary or a custom profile folder, pass `--profile-dir "<folder>"`.

### Option B: a Chrome with a debugging port

Chrome does not open a debugging port on your default profile, so start a separate one, sign in to Substack there once, and connect to it:

```bash
# macOS
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-substack"
# Linux
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.chrome-substack"
# Windows
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\.chrome-substack"

substack-mcp connect --cdp http://127.0.0.1:9222
```

`--cdp` also takes a `ws://` DevTools URL, for example of a Chrome on another machine reached over an SSH tunnel.

### Option C: paste the cookie by hand

For a server with no Chrome: in Chrome open DevTools on substack.com, **Application > Cookies > https://substack.com**, copy the value of `substack.sid`, then:

```bash
substack-mcp connect --token          # paste it, input is hidden
# or, without a session file:
export SUBSTACK_AUTH_TOKEN=...
```

A pasted token is not refreshed on its own. Paste a new one when Substack signs you out.

Check the session at any time:

```bash
substack-mcp status
```

## MCP server

The MCP server lists every tool with its input schema, a description written for agents, and hints: read tools are marked read-only, and tools that publish, message or delete are marked so your client asks before running them.

### Claude Code

```bash
claude mcp add substack -- uvx --from substack-api-mcp substack-mcp mcp
# read only:
claude mcp add substack -- uvx --from substack-api-mcp substack-mcp mcp --read-only
```

### Claude Desktop

`~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "substack": {
      "command": "uvx",
      "args": ["--from", "substack-api-mcp", "substack-mcp", "mcp"]
    }
  }
}
```

### Cursor

`~/.cursor/mcp.json`, the same block as Claude Desktop. A ready copy is in [`mcp.json`](mcp.json).

### Codex

`~/.codex/config.toml`:

```toml
[mcp_servers.substack]
command = "uvx"
args = ["--from", "substack-api-mcp", "substack-mcp", "mcp"]
```

### Over HTTP

`substack-mcp serve` also serves MCP over streamable HTTP at `http://127.0.0.1:8787/mcp`, for clients that take a URL:

```bash
substack-mcp serve
claude mcp add --transport http substack http://127.0.0.1:8787/mcp
```

Then ask your agent things like:

> *Turn essay.md into a draft for everyone and schedule it for Tuesday 8:00 New York time. Once it is out, post a Note with a link card to it.*
>
> *Find comments on my last three posts that I have not answered and draft a short reply to each.*
>
> *Last week's numbers: new and paid subscribers, cancellations, revenue, and opens for each post.*
>
> *Where did my readers come from in the last 30 days?*

## REST API

```bash
substack-mcp serve                    # http://127.0.0.1:8787, MCP at /mcp, docs at /docs
```

Each tool has its own route under `/api/v1/substack`, the same paths as the hosted API at cotlet.dev, so code written against one works with the other. Path parts and the query string are arguments, and a JSON body adds the rest.

```bash
curl 'http://127.0.0.1:8787/api/v1/substack/posts?status=scheduled'
curl 'http://127.0.0.1:8787/api/v1/substack/stats?period=30d'
curl -X POST http://127.0.0.1:8787/api/v1/substack/drafts \
  -H 'Content-Type: application/json' \
  -d '{"title": "Notes on pricing", "body_markdown": "## Why I raised prices\n\nThree reasons..."}'
```

Any tool by name, body as its arguments:

```bash
curl -X POST http://127.0.0.1:8787/api/v1/substack/tools/list_comments -d '{"post_id": "148213977"}'
```

- `GET /api/v1/substack/tools`: every tool with its route, input schema and an example answer.
- `GET /docs`: interactive OpenAPI docs, `GET /openapi.json` the schema, for n8n, Postman or a generated client.
- Answers are JSON. Lists return `next_cursor`; pass it back as `cursor` for the next page.

The server listens on `127.0.0.1` only. To reach it from another device of yours, set a token, and every request then needs `Authorization: Bearer <token>`:

```bash
SUBSTACK_MCP_TOKEN=$(openssl rand -hex 24) substack-mcp serve --host 0.0.0.0
```

## Python and the example scripts

Straight from Python, no server needed:

```python
from substack_api_mcp import call
from substack_api_mcp.scripting import paginate, write_rows

posts = list(paginate("list_posts", {"status": "published"}, "posts"))
write_rows(posts, "posts.csv")
draft = call("create_draft", title="Notes on pricing", body_markdown="Three reasons...")
call("schedule_post", post_id=draft["post_id"], publish_at="2026-11-03T08:00:00-05:00")
```

Or one tool from the shell: `substack-mcp call get_post_stats post_id=148213977`, or with a JSON object.

Ready scripts in [`examples/`](examples/). Each prints JSON, takes `--out file.csv` or `--out file.json` where it makes sense, and `--help`:

| Script | What it does |
|---|---|
| [`draft_from_markdown.py`](examples/draft_from_markdown.py) | A `.md` file to a draft: the first heading is the title, headings, links and lists are kept. `--publish-at` schedules it. |
| [`schedule_post.py`](examples/schedule_post.py) | Schedules a draft for a set time, or `--cancel` takes it back to drafts. |
| [`publish_note.py`](examples/publish_note.py) | A Note now or at a set time, `--link-latest` adds a link card to your newest post. |
| [`list_posts.py`](examples/list_posts.py) | Published, draft or scheduled posts: title, audience, dates, URL. |
| [`get_post.py`](examples/get_post.py) | One post saved as a Markdown file. |
| [`weekly_report.py`](examples/weekly_report.py) | New and paid subscribers, cancellations, revenue, and each new post's opens and new subscribers. |
| [`post_stats.py`](examples/post_stats.py) | Opens, open rate, views, likes, restacks and new subscribers for your last N posts. |
| [`daily_stats.py`](examples/daily_stats.py) | Subscribers, paid subscribers, followers and views day by day. |
| [`traffic_sources.py`](examples/traffic_sources.py) | Where your visitors came from, most views first. |
| [`unanswered_comments.py`](examples/unanswered_comments.py) | Comments on your last N posts that you have not replied to. |
| [`reply_to_comment.py`](examples/reply_to_comment.py) | A reply under one comment. |
| [`list_subscribers.py`](examples/list_subscribers.py) | Subscribers by plan or join date, with activity rating. |
| [`export_subscribers.py`](examples/export_subscribers.py) | The full list as the CSV that Export gives in the dashboard. |
| [`add_subscribers.py`](examples/add_subscribers.py) | Adds emails from a text or CSV file as free subscribers, after asking you. |

```bash
python examples/draft_from_markdown.py essay.md --publish-at 2026-11-03T08:00:00-05:00
python examples/unanswered_comments.py --last 3 --out todo.csv
```

On a schedule, cron on your own computer works while it is on: `0 8 * * 1 cd ~/substack-api-mcp-server && .venv/bin/python examples/weekly_report.py`.

## All 50 tools

`post_id` comes from `list_posts`, `comment_id` from `list_comments`. `substack-mcp tools` prints this list, `substack-mcp tools --json` adds the input schemas.

### Posts and drafts

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_posts` | read | `GET /posts` | Posts of your publication, newest first, with status and audience. |
| `get_post` | read | `GET /posts/{post_id}` | Full post: title, subtitle, body as Markdown, audience, URL and dates. |
| `create_draft` | write | `POST /drafts` | New draft from Markdown. Nothing is sent until you publish or schedule it. |
| `update_draft` | write | `PATCH /drafts/{post_id}` | Change the title, subtitle, body or audience of a draft. |
| `duplicate_post` | write | `POST /posts/{post_id}/duplicate` | Copy any post into a new draft. |
| `delete_post` | write | `DELETE /posts/{post_id}` | Delete a draft, scheduled or published post, with its comments. |

### Publishing

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `publish_post` | write | `POST /posts/{post_id}/publish` | Publish a draft now. |
| `schedule_post` | write | `PUT /posts/{post_id}/schedule` | Publish a draft at a set time, on the web and by email. |
| `cancel_scheduled_post` | write | `DELETE /posts/{post_id}/schedule` | Stop a scheduled post from going out; it stays as a draft. |
| `unpublish_post` | write | `DELETE /posts/{post_id}/publish` | Take a published post off the web and back to drafts. |

### Sections and post tags

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_sections` | read | `GET /sections` | Sections of your publication, the separate newsletters inside it. |
| `list_post_tags` | read | `GET /post-tags` | Tags your publication uses to group posts. |
| `create_post_tag` | write | `POST /post-tags` | New tag for grouping your posts. |
| `tag_post` | write | `PUT /posts/{post_id}/tags/{tag_id}` | Add a tag to a post, or take it off. |

### Comments

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_comments` | read | `GET /posts/{post_id}/comments` | Comments on a post, with author, text and whether you replied. |
| `reply_to_comment` | write | `POST /comments/{comment_id}/replies` | Reply as you under a comment on your post. |
| `pin_comment` | write | `PUT /comments/{comment_id}/pin` | Pin a comment to the top of your post's comments, or unpin it. |
| `like_comment` | write | `PUT /comments/{comment_id}/like` | Like or unlike a comment or a Note as you. |
| `remove_comment` | write | `POST /comments/{comment_id}/remove` | Remove someone's comment from your post as the publication's moderator. |
| `delete_comment` | write | `DELETE /comments/{comment_id}` | Delete one of your own comments, Notes or Note replies. |

### Notes

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_notes` | read | `GET /notes` | Notes posted by you or any other Substack user, newest first, with likes and replies. |
| `list_note_replies` | read | `GET /notes/{note_id}/replies` | Replies under a Note, with author, text and likes. |
| `publish_note` | write | `POST /notes` | Short post in Substack Notes, now or at a set time, optionally with a link card to one of your posts. |
| `reply_to_note` | write | `POST /notes/{note_id}/replies` | Reply as you under any Note or Note reply. |

### Subscribers

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_subscribers` | read | `GET /subscribers` | Subscribers with plan, start date and activity rating. |
| `add_subscriber` | write | `POST /subscribers` | Add one email to your list as a free subscriber. |
| `remove_subscriber` | write | `DELETE /subscribers/{email}` | Remove one email from your subscriber list. |
| `export_subscribers` | read | `GET /subscribers/export` | The full subscriber list as a CSV download link, with the row count. |
| `list_subscriber_tags` | read | `GET /subscriber-tags` | Tags you use to group subscribers. |
| `create_subscriber_tag` | write | `POST /subscriber-tags` | New private tag for grouping subscribers. |
| `tag_subscribers` | write | `POST /subscriber-tags/{tag_id}/subscribers` | Put a tag on subscribers by email, or take it off. |

### Stats

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `get_publication_stats` | read | `GET /stats` | Total and paid subscribers, new subscribers, paid cancellations and estimated revenue for a period. |
| `get_daily_stats` | read | `GET /stats/daily` | Day by day: total and paid subscribers, followers and views. |
| `get_audience_insights` | read | `GET /audience` | Where your subscribers live, and which publications share your readers. |
| `list_traffic_sources` | read | `GET /traffic-sources` | Where your publication's visitors came from in a period, most views first. |
| `get_post_stats` | read | `GET /posts/{post_id}/stats` | Recipients, opens, open rate, views, likes, restacks and subscribers gained. |
| `get_post_traffic` | read | `GET /posts/{post_id}/traffic` | Where a post's readers came from: sources, categories and devices. |
| `get_post_engagement` | read | `GET /posts/{post_id}/engagement` | Who liked and commented on a post, and the subscribers it won and lost. |

### Recommendations

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `list_recommendations` | read | `GET /recommendations` | Publications you recommend, or that recommend you, with the subscribers each sent. |
| `recommend_publication` | write | `PUT /recommendations/{publication_id}` | Recommend another publication to your readers, or stop recommending it. |

### Reader, feed and messages

| Tool | Access | REST route | What it does |
|---|---|---|---|
| `get_feed` | read | `GET /feed` | Your Substack home feed: posts and Notes, For you or Following. |
| `search_substack` | read | `GET /search` | Search all of Substack for people, posts and Notes. |
| `list_activity` | read | `GET /activity` | Your Substack notifications: replies, likes, new followers, restacks, newest first. |
| `get_unread_counts` | read | `GET /unread-counts` | How many unread direct messages, message requests and activity notifications you have. |
| `list_conversations` | read | `GET /conversations` | Your direct-message conversations, latest first, with the last message. |
| `get_conversation` | read | `GET /conversations/{conversation_id}` | The latest messages of one direct-message conversation, oldest first. |
| `send_message` | write | `POST /messages` | Send a direct message on Substack, in a conversation or to a person. |
| `follow_user` | write | `PUT /users/{user}/follow` | Follow or unfollow a Substack user, so their Notes reach your feed. |
| `like_post` | write | `PUT /posts/{post_id}/like` | Like or unlike any Substack post as you. |
| `list_subscriptions` | read | `GET /subscriptions` | Publications you subscribe to, with your plan and whether their emails reach you. |

Never built, on purpose: your Substack sign-in, email, profile and account settings, your publication's address or ownership, and anything that moves money (paid plans, payouts, comps). Every request passes a guard that refuses writes to those Substack paths.

## Configuration

| Variable | Default | What it does |
|---|---|---|
| `SUBSTACK_MCP_HOME` | `~/.config/substack-api-mcp` | Folder of `session.json`. |
| `SUBSTACK_AUTH_TOKEN` | | Substack `substack.sid` cookie, instead of `substack-mcp connect`. |
| `SUBSTACK_PROXY` | | Proxy for every request to Substack, e.g. `http://user:pass@host:port`. |
| `SUBSTACK_MCP_READ_ONLY` | | `1` hides and refuses every tool that changes Substack (same as `--read-only`). |
| `SUBSTACK_MCP_TOKEN` | | Bearer token required by `serve`; needed to listen beyond `127.0.0.1`. |
| `SUBSTACK_MCP_HOST`, `SUBSTACK_MCP_PORT` | `127.0.0.1`, `8787` | Address of `serve`. |

## Security and your Substack account

- **No password anywhere.** Substack signs in by an emailed code. Only cookies are read, and only those of substack.com.
- **The session file is yours.** `session.json` is created with mode 0600. Anyone who has it can act as you on Substack, so keep it out of git and shared folders.
- **Local by default.** `serve` binds to `127.0.0.1` and refuses another address without `SUBSTACK_MCP_TOKEN`.
- **substack.com only.** Requests and redirects outside substack.com and its subdomains are refused.
- **Read-only mode.** `--read-only` or `SUBSTACK_MCP_READ_ONLY=1` exposes the 25 read tools only.
- **Actions reach real people.** Published and scheduled posts are emailed to your subscribers, and Notes, comments, replies and DMs go out under your name. MCP clients ask before running them; a script does not, so try it on a test publication first.
- **Add only people who asked.** `add_subscriber` sends Substack's welcome email. Importing people who did not sign up breaks Substack's rules.

## Errors

The REST API answers `{"error": "<code>", "message": "..."}`. The MCP server returns the same code and message as a tool error.

| Status | Code | What to do |
|---|---|---|
| 401 | `auth_required`, `auth_expired` | No session, Substack signed you out, or it asks you to sign in again before a sensitive action (subscriber lists). Sign out and in at substack.com in Chrome, then run `substack-mcp connect`. |
| 403 | `app_permission_denied` | Your role in the publication cannot do this. |
| 403 | `scope_denied` | The server runs read-only, or the call would change your account settings. |
| 403 | `target_blocked` | Substack refused the request or showed a bot check. Open substack.com in Chrome once, then retry. |
| 409 | `captcha_required` | Substack asks for a CAPTCHA. Solve it in Chrome. |
| 422 | `invalid_input` | An argument is missing or wrong; the message names it. |
| 429 | `rate_limited` | Substack is limiting the account. Wait a few minutes. |
| 502 | `target_error` | Substack answered with an error, or changed its site. `git pull` for the latest tools, or [open an issue](https://github.com/cotletdev/substack-api-mcp-server/issues). |

## Self-hosted or hosted

| | This repo | [Cotlet, hosted](https://cotlet.dev/integrations/substack-api-mcp-server) |
|---|---|---|
| Tools | the same 50 | the same 50 |
| Runs | on your computer, while it is on | in the cloud, 24/7 |
| Substack session | your Chrome, cookies in a local file | your own Cloud Browser in the EU, profile encrypted with AES-256-GCM |
| When Substack changes its site | `git pull` once we have fixed it | fixed for you, every tool tested daily |
| Approvals | your MCP client asks per call | posts, Notes, replies and DMs wait for your OK, switchable per tool |
| Works with | MCP clients on your machine, local scripts | Claude.ai and ChatGPT connectors, n8n, Make, Zapier, any HTTP client |
| Who may use it | you, for noncommercial use | teams, businesses, agencies |
| Price | free | free 7-day trial with 2,000 credits, no card; then one-time packs from $29 for 5,000 credits |

On the hosted version a successful call uses 20 to 30 credits (25 for most tools), failed calls are free, and the Cloud Browser uses 50 credits a day while it has an app enabled for agents. [Full pricing](https://cotlet.dev/pricing).

## FAQ

**Does Substack have an official API?**
Only a limited one (checked 11 Oct 2026). Its Developer API looks up public creator profiles after approval, and there is no public API to write posts or Notes, manage subscribers or send email. RSS reads public posts only. Details and sources: [cotlet.dev/integrations/substack-api-mcp-server](https://cotlet.dev/integrations/substack-api-mcp-server).

**Is there a Substack MCP server for Claude, ChatGPT or Cursor?**
Yes, this one runs on your machine: `substack-mcp mcp` for Claude Code, Claude Desktop, Cursor and Codex. ChatGPT and Claude.ai connectors need a public HTTPS URL, which the [hosted Substack MCP server](https://cotlet.dev/integrations/substack-api-mcp-server) gives you.

**Can I schedule Substack posts from Markdown?**
Yes: `python examples/draft_from_markdown.py essay.md --publish-at 2026-11-03T08:00:00-05:00`. The Substack editor does not import Markdown. The script sends the file as a draft with its headings, bold text, links, lists and code blocks, then schedules it. Images have to be public URLs.

**Can it schedule Notes as well as posts?**
Yes. `publish_note` takes a `publish_at` time and the Note waits in your scheduled Notes until then. A link card needs a published post.

**Can I export my Substack subscribers to CSV?**
Yes: `python examples/export_subscribers.py --out subscribers.csv` gives the same CSV as Export in the subscriber dashboard. `list_subscribers.py --plan paid` or `--since 2026-10-01` gives a filtered list with plan, join date and activity rating.

**Can I export my posts as Markdown?**
Yes, one at a time with `examples/get_post.py --post-id <id> --out post.md`, including the paywalled part and drafts of your own publication. `list_posts.py` gives the IDs.

**Is this a Substack scraper?**
It does what people want a scraper for (export posts, subscribers and stats) but does not parse HTML in a headless browser. It calls the same JSON endpoints the Substack web app calls, in your own account and publication.

**Why does it need my Chrome?**
To read your Substack session. Substack signs in by an emailed code, so there is no password to give it anyway. Chrome is used once per sign-in, not for each call.

**What happens when Substack signs me out?**
Calls fail with `auth_expired`. With Chrome remote debugging on, the server reads the new cookies on the next call (click Allow when Chrome asks); otherwise run `substack-mcp connect` again. Subscriber lists sometimes ask for a fresh sign-in even with a valid session: sign out and in again at substack.com, then `connect`.

**Does it need a paid Substack plan?**
No. Revenue, paid subscribers and cancellations exist only for publications with paid subscriptions.

**Can it email all my subscribers?**
Only by publishing or scheduling a post, the way the editor sends it. Substack emails a post once; edits after the send show on the web and in the app.

**Can it run on a VPS or in Docker?**
Technically yes, with `SUBSTACK_AUTH_TOKEN`. Substack then sees your session from a datacenter IP, which looks less like you. For an always-on setup the hosted version keeps your session in your own Cloud Browser on a fixed IP.

**Will my Substack account get banned?**
Requests carry Chrome's fingerprint and go out one at a time, as you would click. Nobody can promise a platform never acts. Keep to your normal use and do not add or message people in bulk.

**Can I use it at work or for my clients?**
No, the license allows noncommercial use only. For a team, a company or client work, use [Cotlet](https://cotlet.dev) or write to [contact@cotlet.dev](mailto:contact@cotlet.dev).

**Is it open source?**
The source is public, the license is not an open source license: noncommercial use only, no business use.

**A tool broke or I need another one.**
[Open an issue](https://github.com/cotletdev/substack-api-mcp-server/issues) with the tool name and the error message.

## License

[PolyForm Noncommercial License 1.0.0](LICENSE). In short:

- **Allowed:** noncommercial use: you, for your own personal purposes with your own Substack account, or a charity, school, public research or government body. Changing the code, and sharing it under the same license.
- **Not allowed:** any commercial use, your own business included; client work; selling or offering it, or a service built on it.

Earlier versions of this repo (the scripts for the hosted API, up to commit 4399e88) stay MIT.

---

<p>
  <a href="https://cotlet.dev">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/logo-white.svg">
      <img src="assets/logo.svg" alt="Cotlet" width="120">
    </picture>
  </a>
</p>

Maintained by [Cotlet](https://cotlet.dev) ([@cotletdev](https://x.com/cotletdev)). Substack is a trademark of its owner. This project is unofficial and not affiliated with, endorsed or sponsored by Substack.
