from datetime import datetime, timezone
from typing import List
import httpx
from src.config import logger
from src.models import KpopDailyReport


def build_discord_embeds(report: KpopDailyReport) -> dict:
    """Construct the full Discord webhook payload: pinging content + one embed per category."""
    today_str = datetime.now(timezone.utc).strftime("%B %d, %Y")

    # Plain message content — this is what actually triggers the @everyone ping.
    content = (
        f"@everyone\n"
        f"🇰🇷 **r/kpop Daily Digest** — {today_str}\n"
        f"*AI K-Pop Daily: News, Comebacks & Tours*"
    )

    embeds = []

    # Categories configuration: (items, title, emoji, color)
    categories = [
        (report.comebacks_and_releases, "Comebacks & Releases", "🚀", 0x9B59B6),  # Purple
        (report.tours_and_concerts, "Tours & Concerts", "🎫", 0x3498DB),        # Blue
        (report.industry_news, "Industry News", "📰", 0xE67E22),               # Orange
    ]

    for items, cat_name, emoji, color in categories:
        if not items:
            continue

        embed = {
            "title": f"{emoji} {cat_name}",
            "color": color,
            "fields": []
        }

        for item in items[:5]:
            artist_str = f"**[{item.artist}]** " if item.artist else ""
            field_name = f"{artist_str}{item.title[:256]}"[:256]

            flair_badge = f"`[{item.flair}]` " if item.flair else ""
            source_link = f"[🔗 Read More]({item.post_url})"
            upvote_badge = f" ⬆️ {item.upvotes:,}" if item.upvotes > 0 else ""

            field_value = f"{flair_badge}{item.summary}\n{source_link}{upvote_badge}"[:1024]

            embed["fields"].append({
                "name": field_name,
                "value": field_value,
                "inline": False
            })

        # Spacer field so there's visible breathing room before the next embed
        embed["fields"].append({
            "name": "\u200b",
            "value": "\u200b",
            "inline": False
        })

        embeds.append(embed)

    # Footer/timestamp on the last embed so it doesn't repeat on every category block
    if embeds:
        embeds[-1]["footer"] = {"text": "Powered by Gemini AI & r/kpop | Automated GitHub Action"}
        embeds[-1]["timestamp"] = datetime.now(timezone.utc).isoformat()

    return {
        "content": content,
        "embeds": embeds,
        "allowed_mentions": {
            "parse": ["everyone"]  # required — webhooks suppress mentions unless explicitly allowed
        }
    }


def send_to_discord(webhook_url: str, payload: dict):
    """Send the payload built by build_discord_embeds(), batching embeds in groups of 10."""
    content = payload.get("content")
    embeds = payload.get("embeds", [])
    allowed_mentions = payload.get("allowed_mentions")

    logger.info(f"Sending report with {len(embeds)} embed(s) to Discord Webhook...")

    batch_size = 10
    with httpx.Client(timeout=10.0) as client:
        for i in range(0, max(len(embeds), 1), batch_size):
            chunk = embeds[i:i + batch_size]
            batch_payload = {"embeds": chunk}

            # Only the first message includes the pinging content + allowed_mentions
            if i == 0:
                if content:
                    batch_payload["content"] = content
                if allowed_mentions:
                    batch_payload["allowed_mentions"] = allowed_mentions

            res = client.post(webhook_url, json=batch_payload)
            if res.status_code in [200, 204]:
                logger.info(f"Successfully posted embed chunk {i // batch_size + 1} to Discord!")
            else:
                logger.error(f"Discord Webhook returned status code {res.status_code}: {res.text}")
                res.raise_for_status()