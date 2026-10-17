# Substack API and MCP Server

**Substack API** for Python scripts and a hosted **Substack MCP server** for Claude, ChatGPT, Cursor, Codex and n8n. Turn Markdown files into Substack drafts, schedule posts and Notes, export subscribers and posts, reply to comments you have not answered and pull subscriber, revenue and post stats from your own Substack publication.

Substack has only a limited official API and no official MCP server. This repo gives you both, on top of the **hosted Substack API by [Cotlet](https://cotlet.dev/integrations/substack-api-mcp-server)**: you sign in to Substack once in your own Cloud Browser (a Chrome Cotlet runs for you in the cloud), Cotlet keeps you signed in 24/7, and your AI agent (over MCP) or the Python scripts here (over the REST API) work in your account with one API key.

- **Substack MCP server:** `https://cotlet.dev/mcp/v1`, 14 Substack tools for your AI agent. [Setup](#substack-mcp-server-for-claude-chatgpt-cursor-and-codex)
- **Substack API:** `https://cotlet.dev/api/v1/substack/{endpoint}`, plus 15 ready Python scripts, one file per job, standard library only. [Scripts](#scripts)

[![Substack API docs](https://img.shields.io/badge/Substack%20API-docs-6d4aef)](https://cotlet.dev/docs/api/substack)
[![Substack MCP server](https://img.shields.io/badge/Substack%20MCP%20server-cotlet.dev%2Fmcp%2Fv1-6d4aef)](https://cotlet.dev/docs/mcp)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-141318)](#requirements)
[![No dependencies](https://img.shields.io/badge/dependencies-none-141318)](#requirements)
[![License: MIT](https://img.shields.io/badge/license-MIT-141318)](LICENSE)

```bash
# Substack MCP server for your AI agent (Claude Code)
claude mcp add --transport http cotlet https://cotlet.dev/mcp/v1 \
  --header "Authorization: Bearer $COTLET_API_KEY"

# Substack API from Python
git clone https://github.com/cotletdev/substack-api-mcp-server.git && cd substack-api-mcp-server
export COTLET_API_KEY=cotlet_...          # https://cotlet.dev/app/signup?app=substack
python schedule_post.py --file essay.md --at 2026-10-14T08:00:00-04:00
```

## Contents

- [How it works](#how-it-works)
- [Quick start](#quick-start)
- [Scripts](#scripts)
- [Substack MCP server for Claude, ChatGPT, Cursor and Codex](#substack-mcp-server-for-claude-chatgpt-cursor-and-codex)
- [Run it on a schedule: cron, GitHub Actions, n8n, Make, Zapier](#run-it-on-a-schedule)
- [Substack API endpoints](#substack-api-endpoints)
- [FAQ](#faq)
- [Pricing](#pricing)
- [Security and your Substack account](#security-and-your-substack-account)

## How it works

```text
your script / AI agent ──HTTPS──▶ Cotlet Substack API ──your Cloud Browser's IP and cookies──▶ substack.com (your publication)
```

1. **Get an API key.** [Request access at cotlet.dev](https://cotlet.dev/app/signup?app=substack) with Substack selected. Each request is reviewed and the key arrives by email. Every account starts with a free 7-day trial and 2,000 credits, no card needed.
2. **Sign in to Substack once.** In the Cotlet console, open your Cloud Browser, sign in to Substack there the way you always do, and press **Enable for agents** (read only or read and write). Password saving is off, so Cotlet never saves your password.
3. **Run the scripts.** Each one is a plain `POST https://cotlet.dev/api/v1/substack/{endpoint}` with your key. When Substack changes its site, Cotlet fixes the integration; these scripts keep working unchanged.

Without a key, or before your access is active, the API answers `403` with a link to request access.

## Quick start

### Requirements

- Python 3.9 or newer. No `pip install`: the scripts use only the standard library.
- A Cotlet API key, with Substack enabled for agents in your Cloud Browser.
- A Substack account that can publish to the publication. The scripts can do what that account can do there.

### Setup

```bash
git clone https://github.com/cotletdev/substack-api-mcp-server.git
cd substack-api-mcp-server
cp .env.example .env          # paste your key into .env, or:
export COTLET_API_KEY=cotlet_...
```

### First calls

```bash
python list_posts.py --status scheduled                 # what is already queued
python create_draft.py --file essay.md                  # Markdown file -> Substack draft
python export_subscribers.py --out subscribers.csv
python weekly_report.py
```

## Scripts

Scripts that list things print JSON by default. Add `--out file.csv` or `--out file.json` to save it. Run any script with `--help` for all options.

### Posts, drafts and Notes

| Script | What it does |
|---|---|
| [`create_draft.py`](create_draft.py) | Turns a Markdown file into a Substack draft. The first `#` heading becomes the title, a line under it the subtitle. Warns about local image paths. Sends nothing. |
| [`update_draft.py`](update_draft.py) | Replaces a draft's title, subtitle, body or audience, from a file or flags. |
| [`schedule_post.py`](schedule_post.py) | Schedules a draft, or a Markdown file in one go, for a set time with its time zone. Refuses past times and more than three months out, stops if another post is set for that day, and can schedule a Note with a link card a few hours later. |
| [`publish_post.py`](publish_post.py) | Publishes a draft now, by email and on the web, or `--web-only`. |
| [`publish_note.py`](publish_note.py) | Posts a Note now or at a set time, with a link card to a post or `--link-latest`. |
| [`list_posts.py`](list_posts.py) | Published posts, drafts or scheduled posts, newest first. |
| [`get_post.py`](get_post.py) | One post with its full body as Markdown, including the paywalled part of your own posts. |
| [`export_posts.py`](export_posts.py) | Exports your posts to a folder of `.md` files, one per post. Filter by `--since` or `--status`. |

### Subscribers

| Script | What it does |
|---|---|
| [`export_subscribers.py`](export_subscribers.py) | Exports subscribers to CSV: email, plan, join date and activity rating. Full list as Substack's own export, or filtered by `--plan` and `--since`. |
| [`add_subscribers.py`](add_subscribers.py) | Adds emails from a CSV as free subscribers, or gives a complimentary paid plan with `--plan comp`. Skips people already on the list; `--dry-run` shows who would be added. |

### Comments and stats

| Script | What it does |
|---|---|
| [`unanswered_comments.py`](unanswered_comments.py) | Comments on your last N posts, or the last N days, that you have not answered yet. |
| [`reply_to_comment.py`](reply_to_comment.py) | Replies as you under one comment. |
| [`post_stats.py`](post_stats.py) | Recipients, opens, open rate, views, likes, restacks and new subscribers for recent posts, in one table. Marks posts with under two days of data. |
| [`publication_stats.py`](publication_stats.py) | Total, paid, new and churned subscribers and revenue for 7, 30 or 90 days. |
| [`weekly_report.py`](weekly_report.py) | The Monday report: subscribers, paid churn against the 30-day average, revenue and each post of the week. `--save` adds a week-on-week line. |

### Write your own

[`cotlet_client.py`](cotlet_client.py) is under 200 lines and has everything: auth, pagination, rate-limit retries, confirmations, Markdown files and CSV export.

```python
from cotlet_client import call, paginate

for sub in paginate("list_subscribers", {"plan": "paid", "since": "2026-10-01"}, "subscribers"):
    print(sub["email"], sub["activity_rating"])

draft = call("create_draft", {"title": "Notes on pricing", "body_markdown": "Last month I..."})
call("schedule_post", {"post_id": draft["post_id"], "publish_at": "2026-10-14T08:00:00-04:00"})
```

### Confirmations for actions that reach people

Scheduling and publishing posts, posting Notes, replying to comments and adding subscribers go out under your name. By default each of these calls waits for your OK: the script prints a link, you approve it in the browser, and the script continues. For unattended runs (cron, GitHub Actions), switch confirmation off for the tools you choose in the Cotlet dashboard, for example only for `publish_note`. Creating and updating drafts reaches no one and runs without asking.

## Substack MCP server for Claude, ChatGPT, Cursor and Codex

The same Substack API is a hosted Substack MCP server, so your AI agent can do all of this in plain words. Nothing to install or run: one URL, same key. A ready config is in [`mcp.json`](mcp.json).

```bash
# Claude Code
claude mcp add --transport http cotlet https://cotlet.dev/mcp/v1 \
  --header "Authorization: Bearer $COTLET_API_KEY"
```

```json
// Cursor: ~/.cursor/mcp.json
{
  "mcpServers": {
    "cotlet": {
      "url": "https://cotlet.dev/mcp/v1",
      "headers": { "Authorization": "Bearer ${env:COTLET_API_KEY}" }
    }
  }
}
```

```toml
# Codex: ~/.codex/config.toml
[mcp_servers.cotlet]
url = "https://cotlet.dev/mcp/v1"
bearer_token_env_var = "COTLET_API_KEY"
```

Claude Desktop and ChatGPT: add a custom connector with the URL `https://cotlet.dev/mcp/v1`. Setup for every client: [cotlet.dev/docs/mcp](https://cotlet.dev/docs/mcp).

Then ask:

> *Turn essay.md into a Substack draft for everyone, schedule it for Tuesday 8:00 New York time, and schedule a Note with a link card to it for 12:00 the same day.*
>
> *Find comments on my last three posts that I have not answered and draft a reply to each in my voice.*
>
> *Every Monday at 8:00, send me last week's new free and paid subscribers, churned paid subscribers, revenue, and how each post did.*
>
> *Add everyone from workshop.csv as free subscribers.*

Tools show up as `substack_create_draft`, `substack_schedule_post` and so on.

## Run it on a schedule

| Where | How |
|---|---|
| **cron** | `0 8 * * 1 cd ~/substack-api-mcp-server && python3 weekly_report.py --save last-week.json` |
| **GitHub Actions** | Fork this repo, add the `COTLET_API_KEY` secret and uncomment the schedule in [`.github/workflows/substack-weekly.yml`](.github/workflows/substack-weekly.yml). |
| **n8n** | MCP Client node with `https://cotlet.dev/mcp/v1`, or an HTTP Request node: `POST https://cotlet.dev/api/v1/substack/{endpoint}` with `Authorization: Bearer <key>`. Trigger: Schedule. |
| **Make** | HTTP module, same URL, header and JSON body. Scenario schedule. |
| **Zapier** | Webhooks by Zapier (POST), same URL, header and body. Schedule by Zapier trigger. |
| **Your AI agent** | A scheduled agent run, for example a Claude Code routine, with the MCP server above. |

Cotlet runs in the cloud, so scheduled jobs keep working while your computer is off.

## Substack API endpoints

Base URL `https://cotlet.dev/api/v1/substack`. Every endpoint is a `POST` with a JSON body. Full parameters and example responses: [cotlet.dev/docs/api/substack](https://cotlet.dev/docs/api/substack).

| Endpoint | Access | Description |
|---|---|---|
| `list_posts` | read | Posts of your publication, newest first, with status and audience. |
| `get_post` | read | Full post: title, subtitle, body as Markdown, audience, URL and dates. |
| `get_post_stats` | read | Recipients, opens, open rate, views, likes, restacks and subscribers gained. |
| `get_publication_stats` | read | Total, paid, new and churned subscribers and revenue for a period. |
| `list_subscribers` | read | Subscribers with plan, start date and activity rating. |
| `export_subscribers` | read | The full subscriber list as a CSV download link, valid for 1 hour. |
| `list_comments` | read | Comments on a post, with author, text and whether you replied. |
| `create_draft` | write | New draft from Markdown. Nothing is sent until you publish or schedule it. |
| `update_draft` | write | Change the title, subtitle, body or audience of a draft. |
| `schedule_post` | write, confirm | Publish a draft at a set time, on the web and by email. |
| `publish_post` | write, confirm | Publish a draft now. |
| `publish_note` | write, confirm | Short post in Substack Notes, now or at a set time, optionally with a link card to one of your posts. |
| `reply_to_comment` | write, confirm | Reply as you under a comment on your post. |
| `add_subscriber` | write, confirm | Add an email as a free subscriber or give a complimentary paid plan. |

Raw call, any language:

```bash
curl -X POST https://cotlet.dev/api/v1/substack/list_posts \
  -H "Authorization: Bearer $COTLET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "scheduled"}'
```

### Errors

| Status | Code | What to do |
|---|---|---|
| 403 | `api_key_required`, `access_not_granted` | Set `COTLET_API_KEY`, or [request access to Substack](https://cotlet.dev/app/signup?app=substack). |
| 403 | `AUTH_REQUIRED`, `AUTH_EXPIRED` | Substack is not signed in or not enabled for agents, or it signed you out. Open the `browser_url` in the error, sign in to Substack in your Cloud Browser and enable it. |
| 403 | `CAPTCHA_REQUIRED`, `MFA_REQUIRED` | Substack asked for a check only you can pass. Finish it in your Cloud Browser at the `browser_url`. |
| 403 | `SCOPE_DENIED` | You enabled Substack read only. Switch it to read and write in your Cloud Browser. |
| 402 | `INSUFFICIENT_CREDITS` | Credits ran out. Buy a credit pack in the dashboard. |
| 429 | `rate_limited` | The client waits for `Retry-After` and retries by itself. |
| 503 | `TARGET_BLOCKED` | Substack changed something; the endpoint is paused until it is fixed. Credits are refunded. |

## FAQ

**Does Substack have an official API?**
Only a limited one (checked 11 Oct 2026). Its Developer API looks up public creator profiles after approval, and there is no public API to write posts or Notes, manage subscribers or send email. RSS reads public posts only. Details and sources: [cotlet.dev/integrations/substack-api-mcp-server](https://cotlet.dev/integrations/substack-api-mcp-server).

**Can I schedule Substack posts from Markdown?**
Yes: `python schedule_post.py --file essay.md --at 2026-10-14T08:00:00-04:00`. The Substack editor does not import Markdown; the script sends the file as a draft with its headings, bold text, links and lists, then schedules it. Images have to be URLs.

**Can it schedule Notes as well as posts?**
Yes. `publish_note.py --at ...` puts the Note in your scheduled Notes, and `schedule_post.py --note "..."` schedules one with a link card a few hours after the post goes out.

**Can I export my Substack subscribers to CSV?**
Yes: `python export_subscribers.py --out subscribers.csv` gives the same CSV as Export in the subscriber dashboard. Add `--plan paid` or `--since 2026-10-01` for a filtered list with plan, join date and activity rating.

**Can I export all my Substack posts as Markdown?**
Yes: `python export_posts.py --dir posts` writes one `.md` file per post, including the paywalled part of your own posts. Drafts too, with `--status draft`.

**Is this a Substack scraper?**
It does what people usually want a scraper for (export posts, subscribers and stats) but works differently: the scripts call a hosted API that acts in your own Substack account, signed in inside your own Cloud Browser. There is no headless browser on your machine, no `substack.sid` cookie to copy from DevTools and nothing to fix when Substack updates its site. It works on your own publication, not on other people's.

**Do I have to copy cookies or my Substack password into a config file?**
No. You sign in to Substack once in your own Cotlet Cloud Browser, and enable it for agents. Password saving is off there, so Cotlet never saves your password. Your scripts only ever hold the Cotlet API key.

**What happens when Substack signs me out?**
The call returns `AUTH_EXPIRED` with a link to your Cloud Browser, and you get an email. Sign in to Substack there again and rerun the script.

**Does it need a paid Substack plan?**
No. It acts as the Substack account you sign in with and can do what that account can do in the publication. Paid stats such as churn and revenue exist only for publications with paid subscriptions.

**Can these scripts send an email to all my subscribers?**
Only by publishing or scheduling a post, the way Substack sends it from the editor. Each send waits for your OK by default. Substack emails a post only once; edits after the send show on the web and in the app.

**Can my AI agent reply to comments for me?**
Yes. It finds the comments you have not answered with `list_comments`, drafts replies in your voice, and each `reply_to_comment` call waits for your OK, so you can edit or drop a draft.

**Is this legal?**
You automate your own Substack account with your own login, to do what you could do by hand. Cotlet is unofficial and not affiliated with Substack, does not solve CAPTCHAs or bypass MFA, and pauses an integration within 24 hours if the platform objects. You stay responsible for following Substack's terms and adding only people who agreed to hear from you.

**Can I use it with n8n, Make or Zapier?**
Yes. Use the MCP Client node in n8n, or an HTTP request in any of them: `POST https://cotlet.dev/api/v1/substack/{endpoint}` with your key. See [Run it on a schedule](#run-it-on-a-schedule).

**Is there a Substack MCP server? Can I use it with Claude, ChatGPT or Cursor?**
Yes. Add the hosted Substack MCP server `https://cotlet.dev/mcp/v1`. See [Substack MCP server setup](#substack-mcp-server-for-claude-chatgpt-cursor-and-codex).

**How is this different from open-source Substack MCP servers?**
Community Substack MCP servers on GitHub run on your computer with a session cookie copied from your browser into a config file, and stop working when Substack changes its site until you or the maintainer fix them. Cotlet is hosted, tested daily, keeps your session in an encrypted EU vault, gives you both a REST API and an MCP server with one key, and refunds credits for failed calls. If you would rather run and fix your own code, an open-source server may suit you better.

**What does it cost?**
See [Pricing](#pricing). Failed calls are free.

**Which Python version?**
3.9 or newer. No dependencies.

**My publication is not working / I need another endpoint.**
Email [contact@cotlet.dev](mailto:contact@cotlet.dev) with the `X-Request-Id` from the error, or [open an issue](https://github.com/cotletdev/substack-api-mcp-server/issues).

## Pricing

Free 7-day trial with 2,000 credits, no card needed. Then pay as you go, no subscription: one-time credit packs from $29 for 5,000 credits, valid 12 months, for every app Cotlet supports, Substack included.

A successful call uses 20 to 30 credits (25 for most tools); failed calls cost nothing. Your Cloud Browser uses 50 credits a day while it has an app enabled for agents, however many apps that is. Nothing is charged without a purchase. [Full pricing](https://cotlet.dev/pricing).

## Security and your Substack account

- **No password saved.** You sign in to Substack yourself, in your own Cloud Browser in the EU, where password saving is off. Its profile is stored encrypted with AES-256-GCM.
- **Every background request listed.** Cotlet sends the same requests your browser would, from its IP with its cookies, and lists each one in your Background activity.
- **Scoped access.** Enable Substack for agents read only, or read and write.
- **Your OK first.** Scheduled and published posts, Notes, replies and new subscribers wait for your confirmation unless you switch that off per tool.
- **Cut access in one click.** Disable Substack for agents, sign out of it in your Cloud Browser, or reset the browser.
- **No data kept.** Results pass through to your script and are not stored.
- **Never:** CAPTCHA solving, MFA bypass, spam.

More: [cotlet.dev/security](https://cotlet.dev/security).

## Links

- Substack API and MCP server: [cotlet.dev/integrations/substack-api-mcp-server](https://cotlet.dev/integrations/substack-api-mcp-server)
- Substack API reference: [cotlet.dev/docs/api/substack](https://cotlet.dev/docs/api/substack)
- Substack use cases: [schedule posts from Markdown](https://cotlet.dev/integrations/substack-api-mcp-server/schedule-newsletter-posts), [weekly subscriber and revenue report](https://cotlet.dev/integrations/substack-api-mcp-server/weekly-subscriber-report), [reply to unanswered comments](https://cotlet.dev/integrations/substack-api-mcp-server/reply-to-unanswered-comments)
- All apps without an API on Cotlet: [cotlet.dev/integrations](https://cotlet.dev/integrations)
- Skool API and MCP server: [github.com/cotletdev/skool-api-mcp-server](https://github.com/cotletdev/skool-api-mcp-server)
- About Cotlet: [github.com/cotletdev/cotlet](https://github.com/cotletdev/cotlet)
- Cotlet on X: [@cotletdev](https://x.com/cotletdev)

---

<p>
  <a href="https://cotlet.dev">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="assets/logo-white.svg">
      <img src="assets/logo.svg" alt="Cotlet" width="120">
    </picture>
  </a>
</p>

Maintained by [Cotlet](https://cotlet.dev). Substack is a trademark of its owner. This project is unofficial and not affiliated with, endorsed or sponsored by Substack. Scripts are MIT licensed; using the hosted API requires a Cotlet account and is subject to the [Cotlet terms](https://cotlet.dev/terms).
