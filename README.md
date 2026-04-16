# 📰 Weekly Digest

A free, auto-updating news site that aggregates the week's most important stories across your topics of interest. Built with Python + GitHub Actions + GitHub Pages — zero cost, zero servers.

## Topics covered

| Topic | Sources |
|---|---|
| 🤖 Technology & AI | TechCrunch, MIT Tech Review, Ars Technica, The Verge, VentureBeat, Wired |
| 🌎 Chile & Latin America | BBC LatAm, NYT Americas, Reuters, The Guardian |
| 🌿 Environment & Climate | BBC Science, The Guardian, Yale E360, Inside Climate News |
| 🔬 Science | Science Daily, New Scientist, Nature, BBC Science |
| ✈️ Aviation & Revenue Management | Simple Flying, Reuters Business, The Guardian Business, Aviation Week |

## How it works

1. **GitHub Actions** triggers the Python script every day at 08:00 CLT
2. `fetch_news.py` reads RSS feeds and filters articles by keywords
3. `generate_site.py` builds a static `index.html`
4. The bot commits and pushes the updated files
5. **GitHub Pages** serves the site automatically

## Setup (one-time)

### 1. Create a GitHub account
Go to [github.com](https://github.com) and sign up (free).

### 2. Create a new repository
- Click **+** → **New repository**
- Name it `weekly-digest` (or anything you like)
- Set it to **Public** (required for free GitHub Pages)
- Click **Create repository**

### 3. Upload these files
Upload all files from this folder to the repository root. You can drag & drop them in the GitHub web UI.

The structure should look like:
```
weekly-digest/
├── .github/
│   └── workflows/
│       └── daily.yml
├── data/
│   └── news.json        ← generated automatically
├── fetch_news.py
├── generate_site.py
├── run.py
├── requirements.txt
└── README.md
```

### 4. Enable GitHub Pages
- Go to your repo → **Settings** → **Pages**
- Under **Source**, select **Deploy from a branch**
- Select branch: `main`, folder: `/ (root)`
- Click **Save**
- Your site will be live at `https://YOUR_USERNAME.github.io/weekly-digest/`

### 5. Run it for the first time
- Go to **Actions** tab in your repo
- Click **Daily News Digest** → **Run workflow** → **Run workflow**
- Wait ~1 minute — it will fetch news and generate the site

### 6. Done! 🎉
From now on, the site updates automatically every morning at 08:00 CLT.

## Customizing topics & keywords

Edit `fetch_news.py` — the `TOPICS` dictionary at the top controls everything:
- Add/remove **keywords** to fine-tune filtering
- Add/remove **RSS feed URLs** to change sources
- Change `MAX_ARTICLES_PER_TOPIC` to show more/fewer articles per section

## Changing the update schedule

Edit `.github/workflows/daily.yml` — the `cron` line:
```yaml
- cron: "0 11 * * *"   # 11:00 UTC = 08:00 CLT
```
Use [crontab.guru](https://crontab.guru) to build a custom schedule.

## Local development

```bash
pip install feedparser
python run.py
# then open index.html in your browser
```
