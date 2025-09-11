from __future__ import annotations

from reddit_pipeline.llm.insights import _response_format as munger_schema
from reddit_pipeline.llm.summariser import _response_format as summariser_schema


def test_summariser_schema_shape_has_required_keys():
    schema = summariser_schema()["json_schema"]["schema"]
    required = set(schema["required"])  # type: ignore[index]
    assert {
        "summary",
        "pain_points",
        "recommendations",
        "segments",
        "tools_mentioned",
        "contrarian_take",
        "key_metrics",
        "sources",
    }.issubset(required)


def test_munger_schema_shape_has_required_keys():
    schema = munger_schema()["json_schema"]["schema"]
    required = set(schema["required"])  # type: ignore[index]
    assert {
        "freelancer_actions",
        "client_playbook",
        "measurement",
        "risk_watchouts",
        "draft_titles",
        "confidence",
        "short_rationale",
    }.issubset(required)
