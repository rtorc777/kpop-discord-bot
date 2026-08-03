import json
import time
from typing import List
from src.config import logger
from src.models import KpopDailyReport


def summarize_posts_with_gemini(posts: List[dict], api_key: str) -> KpopDailyReport:
    """Use Gemini API to process and structure raw Reddit posts into categorized summaries."""
    from google import genai
    from google.genai import types

    logger.info("Initializing Gemini API client...")
    client = genai.Client(api_key=api_key)

    # Trim post details to keep prompt lean & fast
    compact_posts = []
    for p in posts[:25]:
        compact_posts.append({
            "title": p.get("title"),
            "url": p.get("url") or p.get("reddit_url"),
            "flair": p.get("flair", "")
        })

    posts_text = json.dumps(compact_posts, indent=2)

    prompt = f"""
You are an expert K-Pop journalist and analyst.
Below is a list of top daily posts from r/kpop in JSON format.

Your task:
1. Analyze the posts and group them into 4 distinct categories:
   - comebacks_and_releases: MVs, Teasers, Tracklists, Concept Photos, Album releases.
   - tours_and_concerts: Tour announcements, concert dates, ticketing info, world tours.
   - industry_news: Agency news, contract updates, chart records, military updates, official statements.
   - highlights_and_discussion: High-performing discussions, variety content, performance clips, achievements.

2. For each category:
   - Pick the top items (up to 5 per category).
   - Clean up titles and write a 1 sentence summary for each item.
   - Identify the primary artist/group involved.
   - Preserve the exact post 'url'.

Raw Posts Data:
{posts_text}
"""

    # List of models supported by active API keys
    models_to_try = [
        "gemini-flash-latest",
        "gemini-flash-lite-latest",
        "gemini-2.5-flash",
        "gemini-2.0-flash-lite",
        "gemini-2.0-flash"
    ]
    last_exception = None

    for model_name in models_to_try:
        logger.info(f"Attempting summarization with Gemini model ({model_name})...")
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=KpopDailyReport,
                    temperature=0.2,
                )
            )
            report = KpopDailyReport.model_validate_json(response.text)
            logger.info(f"Gemini summarization complete using {model_name}!")
            return report
        except Exception as e:
            err_msg = str(e)
            logger.warning(f"Model {model_name} failed: {err_msg}")
            last_exception = e

    logger.error("All Gemini model attempts failed.")
    raise last_exception
