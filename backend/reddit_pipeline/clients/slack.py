"""Slack notifier client placeholder.

Use for alerting or posting summaries to Slack channels.
"""

from __future__ import annotations

from ..utils import get_json_logger, retry_with_backoff

log = get_json_logger("reddit_pipeline.clients.slack")


class SlackClient:
    def __init__(self, bot_token: str | None) -> None:
        self.bot_token = bot_token

    @retry_with_backoff()
    def post_message(self, channel: str, text: str) -> None:
        log.info("Posting Slack message", extra={"channel": channel, "len": len(text)})
        # TODO: Implement via Slack Web API if enabled
