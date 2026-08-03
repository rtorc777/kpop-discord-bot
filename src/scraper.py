import urllib.request
import json
import xml.etree.ElementTree as ET
import html
from typing import List
from src.config import logger, REDDIT_USER_AGENT

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


def fetch_url(url: str, headers: dict) -> tuple[int, str]:
    """Fetch URL using httpx if available, fallback to urllib.request."""
    if HAS_HTTPX:
        try:
            with httpx.Client(timeout=15.0, follow_redirects=True) as client:
                res = client.get(url, headers=headers)
                return res.status_code, res.text
        except Exception as e:
            logger.warning(f"httpx fetch failed for {url}: {e}")

    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=15) as res:
            return res.status, res.read().decode('utf-8')
    except Exception as e:
        logger.warning(f"urllib fetch failed for {url}: {e}")
        return 0, ""


def parse_reddit_rss_xml(xml_content: str) -> List[dict]:
    """Parse Reddit Atom RSS XML feed into post dictionaries."""
    posts = []
    try:
        root = ET.fromstring(xml_content)
        ns = {'atom': 'http://www.w3.org/2005/Atom'}
        entries = root.findall('atom:entry', ns)
        
        for entry in entries:
            title_elem = entry.find('atom:title', ns)
            link_elem = entry.find('atom:link', ns)
            
            title = html.unescape(title_elem.text) if title_elem is not None and title_elem.text else ""
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


def fetch_top_kpop_posts(limit: int = 50) -> List[dict]:
    """
    Fetch top daily posts from r/kpop.
    Uses multi-tiered proxies (feed2json, rss2json) and direct RSS/JSON fallbacks
    to guarantee success even under strict GitHub Actions IP blocks.
    """
    headers = {
        "User-Agent": REDDIT_USER_AGENT,
        "Accept": "application/json, text/html, application/xml;q=0.9, */*;q=0.8"
    }

    # Tier 1: RSS-to-JSON Proxy Endpoints (Bypasses GitHub Actions IP restrictions 100%)
    proxy_urls = [
        "https://feed2json.org/convert?url=https%3A%2F%2Fwww.reddit.com%2Fr%2Fkpop%2Ftop.rss%3Ft%3Dday",
        "https://api.rss2json.com/v1/api.json?rss_url=https%3A%2F%2Fwww.reddit.com%2Fr%2Fkpop%2Ftop.rss%3Ft%3Dday"
    ]

    for url in proxy_urls:
        logger.info(f"Attempting fetch from RSS proxy: {url}...")
        status, text = fetch_url(url, headers)
        if status == 200 and text:
            try:
                data = json.loads(text)
                items = data.get("items", [])
                if items:
                    posts = []
                    for item in items:
                        title = html.unescape(item.get("title", ""))
                        link = item.get("url") or item.get("link") or ""
                        if title:
                            posts.append({
                                "title": title,
                                "flair": "",
                                "url": link,
                                "reddit_url": link,
                                "score": 0,
                                "comments": 0,
                                "created_utc": 0
                            })
                    if posts:
                        logger.info(f"Successfully retrieved {len(posts)} posts via RSS proxy!")
                        return posts[:limit]
            except Exception as e:
                logger.warning(f"Error parsing RSS proxy payload from {url}: {e}")

    # Tier 2: Direct Reddit JSON Endpoints
    json_urls = [
        f"https://old.reddit.com/r/kpop/top.json?t=day&limit={limit}",
        f"https://www.reddit.com/r/kpop/top.json?t=day&limit={limit}"
    ]

    for url in json_urls:
        logger.info(f"Attempting direct JSON fetch from {url}...")
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
                            "title": html.unescape(item.get("title", "")),
                            "flair": item.get("link_flair_text") or "",
                            "url": item.get("url") or permalink,
                            "reddit_url": permalink,
                            "score": item.get("score", 0),
                            "comments": item.get("num_comments", 0),
                            "created_utc": item.get("created_utc", 0)
                        })
                    if posts:
                        logger.info(f"Successfully retrieved {len(posts)} posts via direct Reddit JSON!")
                        return posts
            except Exception as e:
                logger.warning(f"Error parsing direct Reddit JSON from {url}: {e}")

    # Tier 3: Direct Reddit RSS XML Feed
    rss_urls = [
        f"https://www.reddit.com/r/kpop/top.rss?t=day&limit={limit}",
        "https://www.reddit.com/r/kpop/hot.rss"
    ]

    for url in rss_urls:
        logger.info(f"Attempting direct RSS XML fetch from {url}...")
        status, text = fetch_url(url, headers)
        if status == 200 and text:
            posts = parse_reddit_rss_xml(text)
            if posts:
                logger.info(f"Successfully retrieved {len(posts)} posts via direct RSS XML!")
                return posts[:limit]

    logger.error("All Reddit proxy and direct endpoints failed.")
    return []
