import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _severity_emoji(severity: str) -> str:
    return {"critical": "🔴", "warning": "🟡", "info": "🔵"}.get(severity, "⚪")


def _build_summary(review_data: dict) -> dict:
    score = review_data.get("overall_score")
    findings = review_data.get("findings", [])
    title = review_data.get("pr_title", "Code Review")
    review_id = review_data.get("review_id", "")

    critical = sum(1 for f in findings if f.get("severity") == "critical")
    warnings = sum(1 for f in findings if f.get("severity") == "warning")
    info_count = sum(1 for f in findings if f.get("severity") == "info")

    score_emoji = "🟢" if score and score >= 80 else "🟡" if score and score >= 60 else "🔴"

    return {
        "title": title,
        "review_id": review_id,
        "score": score,
        "score_emoji": score_emoji,
        "critical": critical,
        "warnings": warnings,
        "info": info_count,
        "total": len(findings),
        "summary": review_data.get("summary", ""),
    }


def send_slack_notification(review_data: dict, webhook_url: str | None = None):
    url = webhook_url or settings.SLACK_WEBHOOK_URL
    if not url:
        return

    s = _build_summary(review_data)

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"📋 Review Complete: {s['title']}"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Score:* {s['score_emoji']} {s['score']}/100"},
                {"type": "mrkdwn", "text": f"*Findings:* {s['total']}"},
                {"type": "mrkdwn", "text": f"🔴 {s['critical']} critical  🟡 {s['warnings']} warnings"},
                {"type": "mrkdwn", "text": f"🔵 {s['info']} info"},
            ],
        },
    ]

    if s["summary"]:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Summary:* {s['summary'][:500]}"},
        })

    payload = {"blocks": blocks}

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
        logger.info(f"Slack notification sent for review {s['review_id']}")
    except Exception:
        logger.exception("Failed to send Slack notification")


def send_discord_notification(review_data: dict, webhook_url: str | None = None):
    url = webhook_url or settings.DISCORD_WEBHOOK_URL
    if not url:
        return

    s = _build_summary(review_data)

    embed = {
        "title": f"📋 Review Complete: {s['title']}",
        "color": 0x22c55e if s["score"] and s["score"] >= 80 else 0xf59e0b if s["score"] and s["score"] >= 60 else 0xef4444,
        "fields": [
            {"name": "Score", "value": f"{s['score_emoji']} {s['score']}/100", "inline": True},
            {"name": "Findings", "value": str(s["total"]), "inline": True},
            {"name": "Breakdown", "value": f"🔴 {s['critical']} critical\n🟡 {s['warnings']} warnings\n🔵 {s['info']} info", "inline": True},
        ],
    }

    if s["summary"]:
        embed["description"] = s["summary"][:1000]

    payload = {"embeds": [embed]}

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=payload)
            resp.raise_for_status()
        logger.info(f"Discord notification sent for review {s['review_id']}")
    except Exception:
        logger.exception("Failed to send Discord notification")


def notify_review_complete(review_data: dict, slack_url: str | None = None, discord_url: str | None = None):
    send_slack_notification(review_data, slack_url)
    send_discord_notification(review_data, discord_url)
