import urllib.request
import json
import xml.etree.ElementTree as ET
from typing import List
from src.config import logger, REDDIT_USER_AGENT

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


def parse_reddit_rss(xml_content: str) -> List[dict]:
    """Parse Reddit Atom RSS XML feed into post dictionaries."""
    posts = []
    try:
        root = ET.fromstring(xml_content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)
        
        for entry in entries:
            title_elem = entry.find('atom:title', ns)
            link_elem = entry.find('atom:link', ns)
            
            title = title_elem.text if title_elem is not None else ""
            permalink = link_elem.attrib.get('href', "") if link_elem is not None else ""
            
            if title:
                posts.append({
                    "title": title,
                    "flair": "",
                    "url": permalink,
                    "reddit_url": permalink,
                    "score": 0,
                    "comments": 0,
                    "created_utc": 0
                })
    except Exception as e:
        logger.warning(f"Error parsing RSS XML: {e}")

    return posts


def fetch_url(url: str, headers: dict) -> tuple[int, str]:
    """Fetch URL using httpx if available, fallback to urllib.request."""
    if HAS_HTTPX:
        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                res = client.get(url, headers=headers)
                return res.status_code, res.text
        except Exception as e:
            logger.warning(f"httpx fetch failed for {url}: {e}")

    # Fallback to standard library urllib
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as res:
            return res.status, res.read().decode('utf-8')
    except Exception as e:
        logger.warning(f"urllib fetch failed for {url}: {e}")
        return 0, ""


def fetch_top_kpop_posts(limit: int = 50) -> List[dict]:
    """
    Fetch top daily posts from r/kpop.
    Uses JSON endpoints with fallback to Reddit's RSS Atom feeds to bypass data center blocks.
    """
    headers = {
        "User-Agent": REDDIT_USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5"
    }

    # 1. Try JSON endpoints first
    json_urls = [
        f"https://old.reddit.com/r/kpop/top.json?t=day&limit={limit}",
        f"https://www.reddit.com/r/kpop/top.json?t=day&limit={limit}",
        f"https://old.reddit.com/r/kpop/hot.json?limit={limit}"
    ]

    for url in json_urls:
        logger.info(f"Attempting to fetch JSON from {url}...")
        status, text = fetch_url(url, headers)
        if status == 200 and text:
            try:
                data = json.loads(text)
                children = data.get("data", {}).get("children", [])
                if children:
                    posts = []
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
                    logger.info(f"Successfully retrieved {len(posts)} posts via JSON from {url}!")
                    return posts
            except Exception as e:
                logger.warning(f"Error parsing JSON from {url}: {e}")

    # 2. Fallback to RSS Feeds (Resilient to GitHub Actions IP rate-limiting)
    rss_urls = [
        f"https://www.reddit.com/r/kpop/top.rss?t=day&limit={limit}",
        f"https://old.reddit.com/r/kpop/top.rss?t=day&limit={limit}",
        "https://www.reddit.com/r/kpop/hot.rss"
    ]

    for url in rss_urls:
        logger.info(f"Attempting RSS fallback from {url}...")
        status, text = fetch_url(url, headers)
        if status == 200 and text:
            posts = parse_reddit_rss(text)
            if posts:
                logger.info(f"Successfully retrieved {len(posts)} posts via RSS feed from {url}!")
                return posts

    logger.error("All Reddit JSON and RSS endpoints failed to respond.")
    return []
