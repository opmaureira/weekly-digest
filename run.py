#!/usr/bin/env python3
"""
run.py — entrypoint: fetch news then generate site
"""
from fetch_news import fetch_all
from generate_site import generate_site
import json, os

def main():
    print("═" * 50)
    print("  Weekly Digest — daily update")
    print("═" * 50)

    print("\n📡 Fetching news feeds…\n")
    data = fetch_all()

    os.makedirs("data", exist_ok=True)
    with open("data/news.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("\n💾 Saved data/news.json")

    print("\n🏗  Generating site…")
    generate_site()

    print("\n✅ Done!\n")

if __name__ == "__main__":
    main()
