#!/usr/bin/env python3
"""
Email agent: checks Gmail for important emails from specified senders.
Sends a macOS notification when new emails are found.

Setup:
  1. pip install -r requirements.txt
  2. npx @gongrzhe/server-gmail-autoauth-mcp auth   # one-time Gmail OAuth
  3. Edit IMPORTANT_SENDERS below
  4. Add to cron (runs at 9:05am and 2:05pm on weekdays):
       crontab -e
       5 9  * * 1-5  /usr/bin/python3 "/path/to/check_emails.py" >> "/path/to/email_agent.log" 2>&1
       5 14 * * 1-5  /usr/bin/python3 "/path/to/check_emails.py" >> "/path/to/email_agent.log" 2>&1
"""

import asyncio
import subprocess
import sys
from datetime import datetime, timedelta

# ── Configuration ─────────────────────────────────────────────────────────────

IMPORTANT_SENDERS = [
    # Add the email addresses you want to monitor:
    "someone@example.com",
    "another@example.com",
]

# How many hours back to look (set to slightly more than the gap between checks)
LOOKBACK_HOURS = 6

# ─────────────────────────────────────────────────────────────────────────────

try:
    from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage
except ImportError:
    print("Install dependencies: pip install -r requirements.txt")
    sys.exit(1)


def notify(title: str, body: str) -> None:
    """Send a macOS notification."""
    safe_body = body.replace("\\", "\\\\").replace('"', '\\"')
    safe_title = title.replace("\\", "\\\\").replace('"', '\\"')
    subprocess.run(
        [
            "osascript",
            "-e",
            f'display notification "{safe_body}" with title "{safe_title}" sound name "Mail"',
        ],
        check=False,
    )


async def check_emails() -> None:
    since = datetime.now() - timedelta(hours=LOOKBACK_HOURS)
    since_str = since.strftime("%Y/%m/%d")
    sender_query = " OR ".join(f"from:{s}" for s in IMPORTANT_SENDERS)
    sender_list = ", ".join(IMPORTANT_SENDERS)

    prompt = f"""Search Gmail for unread emails from these senders received after {since_str}:
{sender_list}

Use this Gmail search query: ({sender_query}) after:{since_str} is:unread

For each email found, list:
- From
- Subject
- Time received

If no emails were found, respond with exactly: NO_NEW_EMAILS

Keep your response concise."""

    result = ""
    async for msg in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            mcp_servers={
                "gmail": {
                    "command": "npx",
                    "args": ["-y", "@gongrzhe/server-gmail-autoauth-mcp"],
                }
            },
            max_turns=5,
        ),
    ):
        if isinstance(msg, ResultMessage):
            result = msg.result

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")

    if not result or "NO_NEW_EMAILS" in result:
        print(f"[{timestamp}] No new emails from monitored senders.")
    else:
        print(f"[{timestamp}] Found important emails:\n{result}")
        # Build a short notification summary from the first few lines
        lines = [line.strip() for line in result.splitlines() if line.strip()]
        summary = " | ".join(lines[:3])
        if len(summary) > 120:
            summary = summary[:117] + "..."
        notify("New Important Email", summary)


if __name__ == "__main__":
    asyncio.run(check_emails())
