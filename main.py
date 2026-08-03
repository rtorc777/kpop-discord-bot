#!/usr/bin/env python3
"""
r/kpop Daily AI Reporter Discord Bot
Entrypoint script orchestrating scraping, AI summarization, and Discord publishing.
"""

import sys
import json
import argparse

from src.config import logger, GEMINI_API_KEY, DISCORD_WEBHOOK_URL
from src.scraper import fetch_top_kpop_posts
from src.summarizer import summarize_posts_with_gemini
from src.discord_reporter import build_discord_embeds, send_to_discord


def main():
    parser = argparse.ArgumentParser(description="r/kpop Daily AI Reporter Bot")
    parser.add_argument("--dry-run", action="store_true", help="Print generated report to stdout without sending to Discord")
    args = parser.parse_args()

    if not GEMINI_API_KEY:
        logger.error("GEMINI_API_KEY environment variable is missing!")
        sys.exit(1)

    if not DISCORD_WEBHOOK_URL and not args.dry_run:
        logger.error("DISCORD_WEBHOOK_URL environment variable is missing! (Use --dry-run to test locally without Discord)")
        sys.exit(1)

    # 1. Fetch Reddit posts
    posts = fetch_top_kpop_posts(limit=40)
    if not posts:
        logger.warning("No posts retrieved. Exiting.")
        sys.exit(0)

    # 2. Summarize via Gemini API
    report = summarize_posts_with_gemini(posts, GEMINI_API_KEY)

    # 3. Build Discord Embeds
    embeds = build_discord_embeds(report)

    # 4. Output or Deliver
    if args.dry_run or not DISCORD_WEBHOOK_URL:
        logger.info("=== DRY RUN MODE ENABLED ===")
        print("\nGenerated Report JSON:")
        print(report.model_dump_json(indent=2))
        print("\nGenerated Discord Embeds Payload:")
        print(json.dumps(embeds, indent=2))
    else:
        send_to_discord(DISCORD_WEBHOOK_URL, embeds)


if __name__ == "__main__":
    main()
