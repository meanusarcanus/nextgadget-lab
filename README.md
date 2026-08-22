# ⚡ @nextgadget.lab — Autonomous Scheduled Instagram Review Pipeline

A fully autonomous, production-ready scheduled pipeline that posts high-precision tech gadget reviews on Instagram **3 times a week (Monday, Wednesday, Friday at 10:00 AM EST)** for `@nextgadget.lab` with direct Amazon affiliate integration (`techspecdiges-20`).

---

## 🌟 Core System Architecture

```
                               ┌───────────────────────────────────────────────┐
                               │  1. Amazon Product Intelligence Engine         │
                               │  - Selects 4.3+★, 200+ review tech gadgets   │
                               │  - Generates affiliate link (techspecdiges-20)│
                               └──────────────────────┬────────────────────────┘
                                                      │
                                                      ▼
                               ┌───────────────────────────────────────────────┐
                               │  2. SQLite State Database (gadgets.db)         │
                               │  - Tracks processed ASINs                     │
                               │  - Guarantees zero duplicate reviews          │
                               └──────────────────────┬────────────────────────┘
                                                      │
                                                      ▼
                               ┌───────────────────────────────────────────────┐
                               │  3. Copywriting Synthesis Agent               │
                               │  - Formats @nextgadget.lab technical copy     │
                               │  - Hook, Specs, Pros/Cons, Verdict, CTA       │
                               └──────────────────────┬────────────────────────┘
                                                      │
                                                      ▼
                               ┌───────────────────────────────────────────────┐
                               │  4. 1080x1350 Visual Slide Renderer (Pillow) │
                               │  - Dark mode matte black (#0a0a0c) aesthetic  │
                               │  - Cyan (#00f0ff) & Emerald (#00ff9d) accents │
                               │  - 4 branded portrait carousel slides         │
                               └──────────────────────┬────────────────────────┘
                                                      │
                                       ┌──────────────┴──────────────┐
                                       ▼                             ▼
                    ┌───────────────────────────────┐   ┌───────────────────────────────┐
                    │  5a. Meta Graph API Publish   │   │  5b. Local Staging & Webhook │
                    │  - POST /media (Carousel)     │   │  - Discord / Telegram notify  │
                    │  - POST /media_publish        │   │  - Saves JSON + slide assets  │
                    └──────────────┬────────────────┘   └──────────────┬────────────────┘
                                   │                                   │
                                   └─────────────────┬─────────────────┘
                                                     ▼
                               ┌───────────────────────────────────────────────┐
                               │  6. Dynamic Link-in-Bio Hub Generator         │
                               │  - Self-updating glassmorphism static site    │
                               │  - Deployed to GitHub Pages / Cloudflare      │
                               └───────────────────────────────────────────────┘
```

---

## 🛠️ Codebase Structure

| File | Description |
| :--- | :--- |
| [`main.py`](file:///home/theodisius/Webpage/Projects/AP/main.py) | Master pipeline orchestrator script & CLI entrypoint. |
| [`database.py`](file:///home/theodisius/Webpage/Projects/AP/database.py) | SQLite state store managing ASIN tracking, review logs & published posts. |
| [`amazon_scraper.py`](file:///home/theodisius/Webpage/Projects/AP/amazon_scraper.py) | Product Selection & Intelligence Engine with affiliate link generation. |
| [`content_generator.py`](file:///home/theodisius/Webpage/Projects/AP/content_generator.py) | Technical copywriting synthesis agent (LLM API + built-in high-tech engine). |
| [`image_composer.py`](file:///home/theodisius/Webpage/Projects/AP/image_composer.py) | Pillow graphics engine generating 1080x1350 (4:5) branded carousel slides. |
| [`instagram_publisher.py`](file:///home/theodisius/Webpage/Projects/AP/instagram_publisher.py) | Meta Graph API carousel publisher with CDN upload & Webhook staging fallback. |
| [`bio_hub_generator.py`](file:///home/theodisius/Webpage/Projects/AP/bio_hub_generator.py) | Self-updating dark-mode glassmorphism Link-in-Bio website builder (`site/`). |
| [`.github/workflows/scheduled_posts.yml`](file:///home/theodisius/Webpage/Projects/AP/.github/workflows/scheduled_posts.yml) | GitHub Actions Cron pipeline (`0 15 * * 1,3,5`) for zero-maintenance execution. |
| [`.env.example`](file:///home/theodisius/Webpage/Projects/AP/.env.example) | Environment variable template for credentials and webhooks. |

---

## 🚀 Quickstart & Setup

### 1. Installation

```bash
# Clone repository and enter directory
cd /home/theodisius/Webpage/Projects/AP

# Create virtual environment and install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration (`.env`)

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

```ini
# Meta / Instagram Graph API Configuration
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_account_id
INSTAGRAM_ACCESS_TOKEN=your_long_lived_token

# Affiliate Tag (Default: techspecdiges-20)
AMAZON_AFFILIATE_TAG=techspecdiges-20

# Optional Webhook for manual approval mode
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

---

## 🧪 Execution Commands

### Test Dry-Run (Staging Mode)
Generates copy, 4 carousel slides, updates local database, and updates the link-in-bio site without posting live to Instagram:
```bash
python main.py --dry-run
```

### Target a Specific Amazon ASIN
```bash
python main.py --asin B089QPWYY6 --dry-run
```

### Filter by Category (`smart_home`, `productivity`, `edc_tech`, `audio_desk`)
```bash
python main.py --category edc_tech
```

---

## 📅 Zero-Maintenance Scheduled Execution (GitHub Actions)

The workflow `.github/workflows/scheduled_posts.yml` is configured with the following cron schedule:

```yaml
on:
  schedule:
    # Monday, Wednesday, Friday at 10:00 AM EST (15:00 UTC)
    - cron: '0 15 * * 1,3,5'
```

### Setting Up Secrets in GitHub:
Add the following secrets to your GitHub Repository (*Settings > Secrets and variables > Actions*):
- `INSTAGRAM_BUSINESS_ACCOUNT_ID`
- `INSTAGRAM_ACCESS_TOKEN`
- `AMAZON_AFFILIATE_TAG` (`techspecdiges-20`)
- `IMGBB_API_KEY` (Required for uploading slide images to CDN for Meta Graph API)
- `DISCORD_WEBHOOK_URL` (Optional)

---

## 🔗 Dynamic Link-in-Bio Hub

Every time the pipeline executes, it automatically updates `site/index.html` with product cards containing:
- Direct affiliate link: `https://www.amazon.com/dp/{ASIN}?tag=techspecdiges-20`
- Star ratings & review counts
- Interactive category filter & search bar
- Dark mode glassmorphism UI matching `@nextgadget.lab`

Deploy the `site/` directory directly to **GitHub Pages**, **Cloudflare Pages**, or **Vercel**.
