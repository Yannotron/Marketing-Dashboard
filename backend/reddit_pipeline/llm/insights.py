"""Insights extraction utilities (LLM-backed).

Consumes summariser JSON and returns portfolio-fit insights as strict JSON.
"""

from __future__ import annotations

from typing import Any, cast

import orjson
from openai import OpenAI

from ..config import settings
from ..utils import get_json_logger, retry_with_backoff

log = get_json_logger("reddit_pipeline.llm.insights")


SYSTEM_PROMPT = "You are a senior B2B marketing strategist in the UK."


def _response_format() -> dict[str, Any]:
    return {
        "type": "json_schema",
        "json_schema": {
            "name": "insight_munger_schema",
            "schema": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "freelancer_actions": {"type": "array", "items": {"type": "string"}},
                    "client_playbook": {"type": "array", "items": {"type": "string"}},
                    "measurement": {"type": "array", "items": {"type": "string"}},
                    "risk_watchouts": {"type": "array", "items": {"type": "string"}},
                    "draft_titles": {"type": "array", "items": {"type": "string"}},
                    "confidence": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                    "short_rationale": {"type": "string"},
                },
                "required": [
                    "freelancer_actions",
                    "client_playbook",
                    "measurement",
                    "risk_watchouts",
                    "draft_titles",
                    "confidence",
                    "short_rationale",
                ],
            },
            "strict": True,
        },
    }


@retry_with_backoff()
def _call_openai(messages: list[dict[str, str]]) -> dict[str, Any]:
    client = OpenAI(api_key=settings.openai_api_key)
    chat = cast(Any, client.chat.completions)
    resp = chat.create(
        model=settings.llm_model_munger,
        messages=messages,
        response_format=_response_format(),
        temperature=0.2,
    )
    content = resp.choices[0].message.content or "{}"
    try:
        return cast(dict[str, Any], orjson.loads(content))
    except Exception:
        return {
            "freelancer_actions": [],
            "client_playbook": [],
            "measurement": [],
            "risk_watchouts": [],
            "draft_titles": [],
            "confidence": 0.0,
            "short_rationale": content,
        }


def generate_insights_from_summaries(
    summaries: dict[str, dict[str, Any]]
) -> dict[str, dict[str, Any]]:
    """Generate insights for each post_id given a summariser JSON mapping."""

    log.info("Generating insights", extra={"count": len(summaries)})
    outputs: dict[str, dict[str, Any]] = {}
    for post_id, payload in summaries.items():
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": (
                    "Given the following summariser JSON, return strict JSON with keys: "
                    "freelancer_actions[], client_playbook[], measurement[], risk_watchouts[], "
                    "draft_titles[], plus a confidence 0.0–1.0 and short_rationale.\n\n"
                    + orjson.dumps(payload).decode("utf-8")
                ),
            },
        ]
        result = _call_openai(messages)
        outputs[post_id] = result
    return outputs
