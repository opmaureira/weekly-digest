import feedparser
import json
import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# ── Configuration ─────────────────────────────────────────────────────────────

CHILE_TZ = ZoneInfo("America/Santiago")
LOOKBACK_DAYS = 7  # collect news from last 7 days

TOPICS = {
    "ai_tech": {
        "label": "Technology & AI",
        "icon": "🤖",
        "color": "#6366f1",
        "keywords": ["artificial intelligence", "AI", "machine learning", "LLM",
                     "GPT", "neural network", "deep learning", "OpenAI", "Anthropic",
                     "Google DeepMind", "tech", "software", "robotics", "semiconductor",
                     "chip", "quantum", "cybersecurity"],
        "feeds": [
            "https://feeds.feedburner.com/TechCrunch",
            "https://www.technologyreview.com/feed/",
            "https://feeds.arstechnica.com/arstechnica/technology-lab",
            "https://www.theverge.com/rss/index.xml",
            "https://venturebeat.com/category/ai/feed/",
            "https://www.wired.com/feed/rss",
        ],
    },
    "chile_politics": {
        "label": "Chile & Latin America",
        "icon": "🌎",
        "color": "#ef4444",
        "keywords": ["Chile", "Boric", "Latin America", "Latam", "South America",
                     "Argentina", "Peru", "Colombia", "Brazil", "Venezuela",
                     "Mercosur", "Santiago", "Patagonia"],
        "feeds": [
            "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/Americas.xml",
            "https://feeds.reuters.com/reuters/worldNews",
            "https://www.theguardian.com/world/americas/rss",
        ],
    },
    "environment": {
        "label": "Environment & Climate",
        "icon": "🌿",
        "color": "#22c55e",
        "keywords": ["climate", "environment", "carbon", "emissions", "renewable",
                     "solar", "wind energy", "biodiversity", "deforestation",
                     "ocean", "glacier", "pollution", "sustainability", "COP",
                     "fossil fuel", "green", "ecology"],
        "feeds": [
            "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
            "https://www.theguardian.com/environment/rss",
            "https://e360.yale.edu/feed",
            "https://insideclimatenews.org/feed/",
        ],
    },
    "science": {
        "label": "Science",
        "icon": "🔬",
        "color": "#0ea5e9",
        "keywords": ["science", "research", "study", "discovery", "physics",
                     "biology", "chemistry", "astronomy", "space", "NASA",
                     "medicine", "health", "genetics", "psychology",
                     "neuroscience", "vaccine", "experiment"],
        "feeds": [
            "https://www.sciencedaily.com/rss/all.xml",
            "https://www.newscientist.com/feed/home/",
            "https://www.nature.com/nature.rss",
            "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        ],
    },
    "airnguru": {
        "label": "Aviation & Revenue Management",
        "icon": "✈️",
        "color": "#f59e0b",
        "keywords": ["airline", "aviation", "revenue management", "RM", "pricing",
                     "ancillary", "ancillaries", "fare", "yield", "IATA",
                     "airport", "aircraft", "fleet", "passenger", "OTA",
                     "dynamic pricing", "seat", "booking", "GDS", "NDC",
                     "Amadeus", "Sabre", "LATAM", "Aeromexico", "Copa",
                     "low-cost carrier", "LCC", "loyalty", "frequent flyer"],
        "feeds": [
            "https://simpleflying.com/feed/",
            "https://www.ch-aviation.com/news.php?rss=1",
            "https://feeds.reuters.com/reuters/businessNews",
            "https://www.theguardian.com/business/airlines/rss",
            "https://www.aviationweek.com/rss.xml",
            "https://airinsight.com/feed/",
        ],
    },
}

MAX_ARTICLES_PER_TOPIC = 8

# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_date(entry):
    for attr in ("published_parsed", "updated_parsed"):
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return datetime.now(timezone.utc) - timedelta(days=1)


def is_recent(dt, days=LOOKBACK_DAYS):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    return dt >= cutoff


def matches_keywords(entry, keywords):
    text = " ".join([
        entry.get("title", ""),
        entry.get("summary", ""),
        entry.get("tags", [{}])[0].get("term", "") if entry.get("tags") else "",
    ]).lower()
    return any(kw.lower() in text for kw in keywords)


def clean_summary(entry):
    summary = entry.get("summary", entry.get("description", ""))
    # strip HTML tags simply
    import re
    summary = re.sub(r"<[^>]+>", "", summary)
    summary = re.sub(r"\s+", " ", summary).strip()
    return summary[:300] + ("…" if len(summary) > 300 else "")


# ── Main fetch ────────────────────────────────────────────────────────────────

def fetch_topic(topic_key, config):
    seen_urls = set()
    articles = []

    for feed_url in config["feeds"]:
        try:
            feed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"  [warn] Could not parse {feed_url}: {e}")
            continue

        for entry in feed.entries:
            url = entry.get("link", "")
            if not url or url in seen_urls:
                continue

            dt = parse_date(entry)
            if not is_recent(dt):
                continue

            if not matches_keywords(entry, config["keywords"]):
                continue

            seen_urls.add(url)
            articles.append({
                "title": entry.get("title", "No title"),
                "url": url,
                "summary": clean_summary(entry),
                "source": feed.feed.get("title", feed_url),
                "date": dt.astimezone(CHILE_TZ).strftime("%b %d, %Y"),
                "date_sort": dt.timestamp(),
            })

    # sort newest first, cap
    articles.sort(key=lambda a: a["date_sort"], reverse=True)
    return articles[:MAX_ARTICLES_PER_TOPIC]


def fetch_all():
    result = {}
    for key, config in TOPICS.items():
        print(f"Fetching: {config['label']} …")
        articles = fetch_topic(key, config)
        print(f"  → {len(articles)} articles")
        result[key] = {
            "label": config["label"],
            "icon": config["icon"],
            "color": config["color"],
            "articles": articles,
        }
    return result


if __name__ == "__main__":
    data = fetch_all()
    os.makedirs("data", exist_ok=True)
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\n✅ Saved to data/news.json")
