import os
import json
from typing import List
from src.config import logger
from src.models import KpopDailyReport


def summarize_with_claude(posts_text: str, api_key: str) -> KpopDailyReport:
    """Summarize posts using Anthropic's Claude API."""
    import anthropic

    logger.info("Initializing Anthropic Claude client...")
    client = anthropic.Anthropic(api_key=api_key)

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

Respond strictly with valid JSON conforming to this schema:
{{
  "comebacks_and_releases": [{"title": "", "artist": "", "summary": "", "post_url": "", "upvotes": 0, "flair": ""}],
  "tours_and_concerts": [{"title": "", "artist": "", "summary": "", "post_url": "", "upvotes": 0, "flair": ""}],
  "industry_news": [{"title": "", "artist": "", "summary": "", "post_url": "", "upvotes": 0, "flair": ""}],
  "highlights_and_discussion": [{"title": "", "artist": "", "summary": "", "post_url": "", "upvotes": 0, "flair": ""}]
}}

Raw Posts Data:
{posts_text}
"""

    model_name = "claude-3-5-haiku-latest"
    logger.info(f"Sending request to Claude model ({model_name})...")

    response = client.messages.create(
        model=model_name,
        max_tokens=2048,
        temperature=0.2,
        messages=[{"role": "user", "content": prompt}]
    )

    content_text = response.content[0].text
    # Extract JSON if enclosed in markdown code blocks
    if "```json" in content_text:
        content_text = content_text.split("```json")[1].split("```")[0].strip()
    elif "```" in content_text:
        content_text = content_text.split("```")[1].split("```")[0].strip()

    report = KpopDailyReport.model_validate_json(content_text)
    logger.info("Claude summarization complete!")
    return report


def summarize_with_gemini(posts_text: str, api_key: str) -> KpopDailyReport:
    """Summarize posts using Google's Gemini API."""
    from google import genai
    from google.genai import types

    logger.info("Initializing Gemini API client...")
    client = genai.Client(api_key=api_key)

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


def summarize_posts_with_gemini(posts: List[dict], api_key: str) -> KpopDailyReport:
    """Main AI summarization function supporting Claude & Gemini."""
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    # Trim posts payload
    compact_posts = []
    for p in posts[:25]:
        compact_posts.append({
            "title": p.get("title"),
            "url": p.get("url") or p.get("reddit_url"),
            "flair": p.get("flair", "")
        })

    posts_text = json.dumps(compact_posts, indent=2)

    # Use Claude if ANTHROPIC_API_KEY is provided
    if anthropic_key:
        try:
            return summarize_with_claude(posts_text, anthropic_key)
        except Exception as e:
            logger.warning(f"Claude summarization failed: {e}. Falling back to Gemini...")

    return summarize_with_gemini(posts_text, api_key)
