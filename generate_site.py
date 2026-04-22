import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

CHILE_TZ = ZoneInfo("America/Santiago")

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Weekly Digest · {date}</title>
  <link rel="icon" href="icon.png" />
  <link rel="preconnect" href="https://fonts.googleapis.com" />
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,300;0,9..144,700;1,9..144,300&family=DM+Sans:wght@400;500;600&display=swap" rel="stylesheet" />
  <style>
    /* ── Reset & base ── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    :root {{
      --bg:        #0e0f11;
      --surface:   #16181c;
      --border:    #252830;
      --text:      #e8e9ed;
      --muted:     #7a7f8e;
      --accent:    #f0c040;
    }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background: var(--bg);
      color: var(--text);
      font-family: 'DM Sans', sans-serif;
      font-size: 15px;
      line-height: 1.65;
      min-height: 100vh;
    }}

    /* ── Grain overlay ── */
    body::before {{
      content: '';
      position: fixed; inset: 0;
      background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 200 200' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
      background-size: 200px 200px;
      pointer-events: none;
      z-index: 0;
    }}

    /* ── Header ── */
    header {{
      position: relative;
      z-index: 1;
      padding: 4rem 2rem 3rem;
      text-align: center;
      border-bottom: 1px solid var(--border);
    }}
    .header-label {{
      display: inline-block;
      font-size: 0.7rem;
      font-weight: 600;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--accent);
      margin-bottom: 1rem;
    }}
    h1 {{
      font-family: 'Fraunces', serif;
      font-size: clamp(2.4rem, 6vw, 4.2rem);
      font-weight: 700;
      line-height: 1.1;
      letter-spacing: -0.02em;
      color: var(--text);
    }}
    h1 em {{
      font-style: italic;
      color: var(--accent);
    }}
    .header-meta {{
      margin-top: 1rem;
      color: var(--muted);
      font-size: 0.85rem;
    }}

    /* ── Nav tabs ── */
    nav {{
      position: sticky;
      top: 0;
      z-index: 10;
      background: rgba(14,15,17,0.92);
      backdrop-filter: blur(12px);
      border-bottom: 1px solid var(--border);
      padding: 0 2rem;
      display: flex;
      gap: 0;
      overflow-x: auto;
      scrollbar-width: none;
    }}
    nav::-webkit-scrollbar {{ display: none; }}
    nav a {{
      display: flex;
      align-items: center;
      gap: 0.4rem;
      padding: 1rem 1.2rem;
      color: var(--muted);
      text-decoration: none;
      font-size: 0.82rem;
      font-weight: 500;
      white-space: nowrap;
      border-bottom: 2px solid transparent;
      transition: color 0.2s, border-color 0.2s;
    }}
    nav a:hover {{ color: var(--text); border-color: var(--border); }}
    nav a.active {{ color: var(--accent); border-color: var(--accent); }}

    /* ── Main layout ── */
    main {{
      position: relative;
      z-index: 1;
      max-width: 1100px;
      margin: 0 auto;
      padding: 3rem 2rem 6rem;
    }}

    /* ── Section ── */
    .section {{
      margin-bottom: 4rem;
      scroll-margin-top: 5rem;
    }}
    .section-header {{
      display: flex;
      align-items: baseline;
      gap: 0.75rem;
      margin-bottom: 1.5rem;
      padding-bottom: 0.75rem;
      border-bottom: 1px solid var(--border);
    }}
    .section-icon {{ font-size: 1.4rem; }}
    .section-title {{
      font-family: 'Fraunces', serif;
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--text);
    }}
    .section-count {{
      margin-left: auto;
      font-size: 0.75rem;
      color: var(--muted);
    }}

    /* ── Article grid ── */
    .articles {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
      gap: 1px;
      background: var(--border);
      border: 1px solid var(--border);
    }}

    /* ── Article card ── */
    .card {{
      background: var(--surface);
      padding: 1.4rem;
      display: flex;
      flex-direction: column;
      gap: 0.6rem;
      transition: background 0.2s;
    }}
    .card:hover {{ background: #1c1f26; }}
    .card-source {{
      font-size: 0.68rem;
      font-weight: 600;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--muted);
    }}
    .card-source span {{
      display: inline-block;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      margin-right: 0.4rem;
      vertical-align: middle;
      position: relative;
      top: -1px;
    }}
    .card-title {{
      font-family: 'Fraunces', serif;
      font-size: 1rem;
      font-weight: 700;
      line-height: 1.35;
    }}
    .card-title a {{
      color: var(--text);
      text-decoration: none;
      transition: color 0.15s;
    }}
    .card-title a:hover {{ color: var(--accent); }}
    .card-summary {{
      font-size: 0.82rem;
      color: var(--muted);
      line-height: 1.55;
      flex: 1;
    }}
    .card-footer {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-top: 0.4rem;
    }}
    .card-date {{
      font-size: 0.72rem;
      color: var(--muted);
    }}
    .card-link {{
      font-size: 0.72rem;
      font-weight: 600;
      color: var(--accent);
      text-decoration: none;
      letter-spacing: 0.04em;
    }}
    .card-link:hover {{ text-decoration: underline; }}

    /* ── Empty state ── */
    .empty {{
      padding: 2rem;
      text-align: center;
      color: var(--muted);
      font-size: 0.85rem;
      background: var(--surface);
      border: 1px solid var(--border);
    }}

    /* ── Footer ── */
    footer {{
      position: relative;
      z-index: 1;
      text-align: center;
      padding: 2rem;
      color: var(--muted);
      font-size: 0.75rem;
      border-top: 1px solid var(--border);
    }}

    @media (max-width: 600px) {{
      header {{ padding: 2.5rem 1.2rem 2rem; }}
      main {{ padding: 2rem 1.2rem 4rem; }}
      nav {{ padding: 0 0.8rem; }}
      .articles {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>

<header>
  <div class="header-label">Weekly Intelligence Brief</div>
  <h1>The <em>Digest</em></h1>
  <div class="header-meta">Updated {date} &nbsp;·&nbsp; {total} stories across {topics} topics</div>
</header>

<nav>
{nav_items}
</nav>

<main>
{sections}
</main>

<footer>
  Auto-generated by Weekly Digest · Powered by RSS feeds &amp; Python · Updated daily
</footer>

<script>
  // Highlight active nav on scroll
  const sections = document.querySelectorAll('.section');
  const navLinks = document.querySelectorAll('nav a');
  const observer = new IntersectionObserver(entries => {{
    entries.forEach(e => {{
      if (e.isIntersecting) {{
        navLinks.forEach(a => a.classList.remove('active'));
        const active = document.querySelector(`nav a[href="#${{e.target.id}}"]`);
        if (active) active.classList.add('active');
      }}
    }});
  }}, {{ threshold: 0.3 }});
  sections.forEach(s => observer.observe(s));
</script>
</body>
</html>"""


def build_nav(topics):
    items = []
    for key, data in topics.items():
        items.append(
            f'  <a href="#{key}">{data["icon"]} {data["label"]}</a>'
        )
    return "\n".join(items)


def build_section(key, data):
    articles = data["articles"]
    color = data["color"]
    count = len(articles)

    if not articles:
        cards_html = '<div class="empty">No recent articles found for this topic.</div>'
    else:
        cards = []
        for art in articles:
            cards.append(f"""    <article class="card">
      <div class="card-source">
        <span style="background:{color}"></span>{art['source']}
      </div>
      <div class="card-title">
        <a href="{art['url']}" target="_blank" rel="noopener">{art['title']}</a>
      </div>
      <div class="card-summary">{art['summary']}</div>
      <div class="card-footer">
        <span class="card-date">{art['date']}</span>
        <a class="card-link" href="{art['url']}" target="_blank" rel="noopener">Read →</a>
      </div>
    </article>""")
        cards_html = f'  <div class="articles">\n' + "\n".join(cards) + "\n  </div>"

    return f"""<section class="section" id="{key}">
  <div class="section-header">
    <span class="section-icon">{data['icon']}</span>
    <span class="section-title">{data['label']}</span>
    <span class="section-count">{count} article{'s' if count != 1 else ''}</span>
  </div>
{cards_html}
</section>"""


def generate_site(data_path="data/news.json", output_path="index.html"):
    with open(data_path, encoding="utf-8") as f:
        topics = json.load(f)

    now = datetime.now(ZoneInfo("America/Santiago"))
    date_str = now.strftime("%B %d, %Y · %H:%M CLT")
    total = sum(len(d["articles"]) for d in topics.values())

    nav_html = build_nav(topics)
    sections_html = "\n\n".join(build_section(k, v) for k, v in topics.items())

    html = HTML_TEMPLATE.format(
        date=date_str,
        total=total,
        topics=len(topics),
        nav_items=nav_html,
        sections=sections_html,
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Site generated → {output_path}  ({total} articles, {len(topics)} topics)")


if __name__ == "__main__":
    generate_site()
