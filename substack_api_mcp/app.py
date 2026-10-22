"""Everything the server knows about Substack outside `substack/`: names, domains and the session cookie.

The rest of the package reads these values and never names the app itself.
"""

from __future__ import annotations

NAME = "Substack"
SLUG = "substack"
# The command and the prefix of every environment variable (SUBSTACK_AUTH_TOKEN, SUBSTACK_MCP_TOKEN ...).
CLI = "substack-mcp"
ENV = "SUBSTACK"
# Requests may reach only these hosts and their subdomains. Their cookies are read from Chrome.
# The same session works on every {publication}.substack.com host, where the publisher API lives.
DOMAINS = ("substack.com",)
# Present only while signed in. The first is the cookie a pasted token sets.
SESSION_COOKIES = ("substack.sid",)
COOKIE_DOMAIN = ".substack.com"
LOGIN_URL = "https://substack.com/sign-in"
# A final URL with one of these means the app signed the session out.
LOGGED_OUT_MARKERS = ("/sign-in",)
# An answer with one of these asks you to sign in again before a sensitive action (subscriber data).
RELOGIN_MARKERS = ("reauthentication_required",)
# Paths of your Substack account (profile, settings, sign-in, email subscription settings). Tools may
# read them but never write to them; common password, email and sign-in paths are refused anyway.
ACCOUNT_PATHS = (
    r"^/api/v1/user/profile",
    r"^/api/v1/user-setting",
    r"^/api/v1/user/accept_publisher_agreement",
    r"^/api/v1/email(-login|-otp-login|/)",
    r"^/api/v1/login",
    r"^/api/v1/subscription/email",
    r"^/api/v1/publication/(subdomain|transfer_ownership|archive)",
)
# REST routes live under this path, the same as on cotlet.dev.
API_PREFIX = "/api/v1/substack"
# Prepended to the MCP server's instructions: where an agent starts.
AGENT_START = "Start with list_posts or get_publication_stats: every tool works on the publication you own."
