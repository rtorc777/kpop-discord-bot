# 🇰🇷 r/kpop Daily AI Reporter Discord Bot

An automated tool that uses **Google Gemini AI** to scrape the top daily posts from [r/kpop](https://www.reddit.com/r/kpop/), filter and summarize key announcements into 4 distinct categories (Comebacks & Releases, Tours & Concerts, Industry News, and Highlights), and send beautiful **Discord Embeds** to your Discord server daily using **GitHub Actions** — 100% free of charge!

## 📁 Project Architecture

```
kpop-discord-bot/
├── src/
│   ├── __init__.py
│   ├── config.py           # Environment variables & logger configuration
│   ├── models.py           # Pydantic data schemas (ReportItem, KpopDailyReport)
│   ├── scraper.py          # Reddit post fetcher with endpoint fallbacks
│   ├── summarizer.py       # Gemini AI processing & structured JSON parsing
│   └── discord_reporter.py # Discord Embed formatting & Webhook sender
├── main.py                 # CLI entry point orchestrating the workflow
├── requirements.txt        # Dependencies (google-genai, httpx, pydantic, etc.)
├── .env.example            # Environment template for local testing
├── .github/
│   └── workflows/
│       └── daily-report.yml # Daily cron schedule & manual trigger workflow
└── README.md
```

---

## 🌟 Features

- **Automated Reddit Scraping**: Pulls top daily posts from `r/kpop` directly via Reddit's JSON API.
- **AI-Powered Extraction & Summarization**: Employs Google Gemini (`gemini-2.5-flash`) via structured JSON schema to categorize posts into:
  - 🚀 **Comebacks & Releases** (MVs, Teasers, Album details)
  - 🎫 **Tours & Concerts** (Tour announcements, venue details)
  - 📰 **Industry News** (Contracts, charts, agency statements)
  - 🌟 **Highlights & Discussions** (Community achievements, top variety clips)
- **Rich Discord Formatting**: Generates clean, color-coded Discord embeds with vote counts, artist tags, bullet point summaries, and direct post links.
- **Zero Hosting Costs**: Runs once a day via GitHub Actions cron scheduled job (<1 min execution time).
- **Dry-Run Mode**: Test locally without posting to Discord.

---

## 📋 Prerequisites & Setup (100% Free)

### 1. Get a Free Gemini API Key
1. Visit [Google AI Studio](https://aistudio.google.com/).
2. Sign in with your Google account.
3. Click **"Get API key"** and create a key in a new or existing project.
4. Copy your API Key.

### 2. Create a Discord Webhook
1. Open your Discord server and navigate to the channel where you want the report posted.
2. Click the gear icon (**Edit Channel**) -> **Integrations** -> **Webhooks** -> **New Webhook**.
3. Customize the webhook name (e.g., `K-Pop Daily Reporter`) and copy the **Webhook URL**.

### 3. Add GitHub Secrets
1. Push this repository to your GitHub account.
2. Go to your GitHub repository -> **Settings** -> **Secrets and variables** -> **Actions**.
3. Click **New repository secret** and add:
   - Secret Name: `GEMINI_API_KEY` | Value: *(Your Gemini API key)*
   - Secret Name: `DISCORD_WEBHOOK_URL` | Value: *(Your Discord webhook URL)*

---

## 🚀 Running via GitHub Actions

- **Daily Schedule**: The bot automatically executes once a day at `00:00 UTC` via [.github/workflows/daily-report.yml](.github/workflows/daily-report.yml).
- **Manual Trigger**:
  1. Go to your repository's **Actions** tab on GitHub.
  2. Select **Daily r/kpop AI Reporter**.
  3. Click **Run workflow** -> **Run workflow**.

---

## 💻 Local Setup & Development

### 1. Clone & Install Dependencies
```bash
git clone https://github.com/your-username/kpop-discord-bot.git
cd kpop-discord-bot

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Create `.env` File
Create a `.env` file in the project root (see [.env.example](.env.example)):
```env
GEMINI_API_KEY=your_gemini_api_key_here
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/your/webhook/url
```

### 3. Test Run

#### Dry Run (Does NOT post to Discord):
```bash
python main.py --dry-run
```

#### Full Run (Sends report to your Discord Webhook):
```bash
python main.py
```

---

## 🛠️ Customization

- **Change Run Time**: Edit the cron expression in [.github/workflows/daily-report.yml](.github/workflows/daily-report.yml) (e.g., `cron: '0 12 * * *'` for 12:00 PM UTC).
- **Adjust Number of Reddit Posts**: Change `fetch_top_kpop_posts(limit=40)` in `main.py`.
- **Change AI Model**: Default is `gemini-2.5-flash`. You can change the model string in `summarize_posts_with_gemini` inside `main.py`.

---

## 📄 License
MIT License. Feel free to fork and customize for other subreddits!
