import feedparser
import json
import os
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

# ── Configuration ─────────────────────────────────────────────────────────────

CHILE_TZ = ZoneInfo("America/Santiago")
LOOKBACK_DAYS = 7  # collect news from last 7 days

TOPICS = {
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
    "chile_politics": {
        "label": "Chile & Latin America",
        "icon": "🌎",
        "color": "#ef4444",
        "keywords": ["Chile", "Boric", "Kast", "Latin America", "Latam", "South America",
                     "Argentina", "Peru", "Brazil",
                     "Mercosur", "Santiago", "Patagonia", "Pucón", "Pucon", "Villarrica", "Araucanía"],
        "feeds": [
            "https://feeds.bbci.co.uk/news/world/latin_america/rss.xml",
            "https://rss.nytimes.com/services/xml/rss/nyt/Americas.xml",
            "https://feeds.reuters.com/reuters/worldNews",
            "https://www.theguardian.com/world/americas/rss",
        ],
    },
    "ai_tech": {
        "label": "Technology & AI",
        "icon": "🤖",
        "color": "#6366f1",
        "keywords": ["artificial intelligence", "AI", "machine learning", "LLM",
                     "GPT", "neural network", "deep learning", "OpenAI", "Anthropic",
                     "Google DeepMind", "tech", "software", "robotics", "semiconductor",
                     "chip", "quantum", "cybersecurity", "Claude"],
        "feeds": [
            "https://feeds.feedburner.com/TechCrunch",
            "https://www.technologyreview.com/feed/",
            "https://feeds.arstechnica.com/arstechnica/technology-lab",
            "https://www.theverge.com/rss/index.xml",
            "https://venturebeat.com/category/ai/feed/",
            "https://www.wired.com/feed/rss",
        ],
    },
    "environment": {
        "label": "Environment & Climate",
        "icon": "🌿",
        "color": "#22c55e",
        "keywords": ["climate", "environment", "carbon", "emissions", "renewable",
                     "solar", "wind energy", "biodiversity", "deforestation",
                     "ocean", "glacier", "pollution", "sustainability", "COP",
                     "fossil fuel", "green", "ecology", "regenerativo", "ambiental", "ecológico"],
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

}

MAX_ARTICLES_PER_TOPIC = 6

IMPORTANT_KEYWORDS = [
    "breakthrough", "major", "announces", "launch", "crisis",
    "record", "deal", "investment", "regulation", "law",
    "election", "growth", "decline"
]

SOURCE_PRIORITY = {
    "Reuters": 3,
    "BBC": 3,
    "New York Times": 3,
    "The Guardian": 2,
    "TechCrunch": 2,
    "MIT Technology Review": 2,
}

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

def score_article(entry, source):
    text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    
    score = 0
    
    # Base: siempre suma algo
    score += 1
    
    # Keywords importantes
    for kw in IMPORTANT_KEYWORDS:
        if kw in text:
            score += 2
    
    # Prioridad de fuente
    for s, val in SOURCE_PRIORITY.items():
        if s.lower() in source.lower():
            score += val
    
    return score
    
# ── Main fetch ────────────────────────────────────────────────────────────────

def fetch_topic(topic_key, config):
    seen_urls = set()
    articles = []

    chile_articles = []
    latam_articles = []

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

            source = feed.feed.get("title", feed_url)
            text = (entry.get("title", "") + " " + entry.get("summary", "")).lower()

            article = {
                "title": entry.get("title", "No title"),
                "url": url,
                "summary": clean_summary(entry),
                "source": source,
                "date": dt.astimezone(CHILE_TZ).strftime("%b %d, %Y"),
                "date_sort": dt.timestamp(),
                "score": score_article(entry, source),
            }

            seen_urls.add(url)

            # 👇 separación Chile vs LatAm SOLO para ese topic
            if topic_key == "chile_politics":
                if any(word in text for word in ["chile", "boric", "kast", "santiago", "araucanía", "pucon", "villarrica"]):
                    chile_articles.append(article)
                else:
                    latam_articles.append(article)
            else:
                articles.append(article)

    # 👇 lógica especial Chile
    if topic_key == "chile_politics":
        chile_articles.sort(key=lambda a: (a["score"], a["date_sort"]), reverse=True)
        latam_articles.sort(key=lambda a: (a["score"], a["date_sort"]), reverse=True)

        final_articles = chile_articles[:3] + latam_articles[:3]
        return final_articles

    # 👇 resto de topics con score
    articles.sort(key=lambda a: (a["score"], a["date_sort"]), reverse=True)
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
