from typing import List
import httpx
from src.config import logger, REDDIT_USER_AGENT


def fetch_top_kpop_posts(limit: int = 50) -> List[dict]:
    """Fetch top daily posts from r/kpop via Reddit's JSON API with fallback endpoints."""
    urls = [
        f"https://old.reddit.com/r/kpop/top.json?t=day&limit={limit}",
        f"https://www.reddit.com/r/kpop/top.json?t=day&limit={limit}"
    ]
    headers = {
        "User-Agent": REDDIT_USER_AGENT
    }

    data = None
    with httpx.Client(timeout=15.0, follow_redirects=True) as client:
        for url in urls:
            logger.info(f"Attempting to fetch posts from {url}...")
            try:
                response = client.get(url, headers=headers)
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Successfully fetched posts from {url}")
                    break
                else:
                    logger.warning(f"Endpoint {url} returned status code {response.status_code}")
            except Exception as e:
                logger.warning(f"Error fetching from {url}: {e}")

    if not data:
        logger.error("All Reddit JSON endpoints failed.")
        return []

    posts = []
    children = data.get("data", {}).get("children", [])
    for child in children:
        item = child.get("data", {})
        if item.get("stickied"):
            continue

        permalink = f"https://www.reddit.com{item.get('permalink')}"
        posts.append({
            "title": item.get("title", ""),
            "flair": item.get("link_flair_text") or "",
            "url": item.get("url") or permalink,
            "reddit_url": permalink,
            "score": item.get("score", 0),
            "comments": item.get("num_comments", 0),
            "created_utc": item.get("created_utc", 0)
        })

    logger.info(f"Successfully processed {len(posts)} posts from r/kpop.")
    return posts
