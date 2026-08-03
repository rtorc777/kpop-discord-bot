import json
from typing import List
from src.config import logger
from src.models import KpopDailyReport


def summarize_posts_with_gemini(posts: List[dict], api_key: str) -> KpopDailyReport:
    """Use Gemini API to process and structure raw Reddit posts into categorized summaries."""
    from google import genai
    from google.genai import types

    logger.info("Initializing Gemini API client...")
    client = genai.Client(api_key=api_key)

    posts_text = json.dumps(posts, indent=2)

    prompt = f"""
You are an expert K-Pop journalist and analyst.
Below is a list of top posts from r/kpop over the past 24 hours in JSON format.

Your task:
1. Analyze the posts and group them into 4 distinct categories:
   - comebacks_and_releases: MVs, Teasers, Tracklists, Concept Photos, Album releases.
   - tours_and_concerts: Tour announcements, concert dates, ticketing info, world tours.
   - industry_news: Agency news, contract updates, chart records, military updates, official statements.
   - highlights_and_discussion: High-performing discussions, variety content, performance clips, achievements.

2. For each category:
   - Pick the most important and high-impact posts (up to 5 top items per category).
   - Clean up titles and write a concise 1-2 sentence informative summary for each item.
   - Identify the primary artist/group involved.
   - Preserve the post_url (use the 'url' or 'reddit_url' provided in the raw data).
   - Retain the upvotes count and flair.

Raw Reddit Posts Data:
{posts_text}
"""

    logger.info("Sending request to Gemini model (gemini-2.5-flash)...")
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=KpopDailyReport,
                temperature=0.2,
            )
        )
        report = KpopDailyReport.model_validate_json(response.text)
        logger.info("Gemini summarization complete!")
        return report

    except Exception as e:
        logger.error(f"Error during Gemini processing: {e}")
        raise
