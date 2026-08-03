from datetime import datetime, timezone
from typing import List
import httpx
from src.config import logger
from src.models import KpopDailyReport


def build_discord_embeds(report: KpopDailyReport) -> List[dict]:
    """Construct formatted Discord Embeds from the KpopDailyReport model."""
    today_str = datetime.now(timezone.utc).strftime("%B %d, %Y")
    embeds = []

    # Main Header Embed
    header_embed = {
        "title": "🇰🇷 r/kpop Daily Digest",
        "description": f"Your daily AI-curated summary of top K-Pop news, comebacks, and tours for **{today_str}**.",
        "color": 0xFF007F,  # Neon Pink
        "footer": {
            "text": "Powered by Gemini AI & r/kpop | Automated GitHub Action"
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    embeds.append(header_embed)

    # Categories: (items, title, emoji, color)
    categories = [
        (report.comebacks_and_releases, "Comebacks & Releases", "🚀", 0x9B59B6),  # Purple
        (report.tours_and_concerts, "Tours & Concerts", "🎫", 0x3498DB),          # Blue
        (report.industry_news, "Industry News", "📰", 0xE67E22),                  # Orange
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
            field_name = f"{artist_str}{item.title[:200]}"

            flair_badge = f"`[{item.flair}]` " if item.flair else ""
            source_link = f"[🔗 Read More]({item.post_url})"
            upvote_badge = f" ⬆️ {item.upvotes:,}" if item.upvotes > 0 else ""

            field_value = f"{flair_badge}{item.summary}\n{source_link}{upvote_badge}"

            embed["fields"].append({
                "name": field_name,
                "value": field_value[:1024],
                "inline": False
            })

        embeds.append(embed)

    return embeds


def send_to_discord(webhook_url: str, embeds: List[dict]):
    """Send embed payloads to a Discord Webhook, batching by 10 (Discord API limit)."""
    logger.info(f"Sending report with {len(embeds)} embeds to Discord Webhook...")

    batch_size = 10
    for i in range(0, len(embeds), batch_size):
        chunk = embeds[i:i + batch_size]
        payload = {"embeds": chunk}

        with httpx.Client(timeout=10.0) as client:
            res = client.post(webhook_url, json=payload)
            if res.status_code in [200, 204]:
                logger.info(f"Successfully posted embed chunk {i // batch_size + 1} to Discord!")
            else:
                logger.error(f"Discord Webhook returned status code {res.status_code}: {res.text}")
                res.raise_for_status()
