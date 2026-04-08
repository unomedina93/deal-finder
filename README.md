# Affiliate Bot

Claude-powered affiliate marketing automation. Runs daily to generate blog posts,
Pinterest pins, social captions, and email newsletter sections for home decor,
furniture, and tools products — then publishes everything automatically.

---

## How It Works

```
GitHub Actions (runs 9 AM daily)
  → picks a product from products/seed_products.json
  → Claude writes: blog post + 5 pin descriptions + social caption + email section
  → publishes blog post to GitHub Pages
  → queues social posts to Buffer (Pinterest, Instagram, Facebook)
  → creates email draft in Beehiiv
  → logs everything to logs/published.json
```

---

## One-Time Setup (do this once)

### Step 1 — Accounts to create (all free)

| Account | URL | Why |
|---------|-----|-----|
| GitHub | github.com (unomedina93) | Hosts the blog + runs the automation |
| Claude API | console.anthropic.com | Powers all content generation (~$5 starter credit) |
| Amazon Associates | associates.amazon.com | Affiliate links + product data |
| Buffer | buffer.com | Schedules social posts |
| Beehiiv | beehiiv.com | Email newsletter |

Also sign up (free):
- ShareASale (shareasale.com) — access to Home Depot affiliate program
- Rakuten Advertising (rakutenadvertising.com) — access to Wayfair affiliate program

---

### Step 2 — Create your GitHub Pages repo

1. Go to github.com and create a new repo named: `unomedina93.github.io/deal-finder`
2. In repo Settings → Pages → Source: set to **GitHub Actions**
3. Push this entire project to that repo

---

### Step 3 — Add GitHub Secrets

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

Add each of these:

| Secret Name | Where to get it |
|-------------|----------------|
| `ANTHROPIC_API_KEY` | console.anthropic.com → API Keys |
| `AMAZON_ASSOCIATE_TAG` | associates.amazon.com → Account Settings |
| `HOME_DEPOT_AFFILIATE_TAG` | ShareASale dashboard (Home Depot program) |
| `WAYFAIR_AFFILIATE_TAG` | Rakuten dashboard (Wayfair program) |
| `BUFFER_ACCESS_TOKEN` | buffer.com/developers → Get Access Token |
| `BEEHIIV_API_KEY` | app.beehiiv.com → Settings → API |
| `BEEHIIV_PUBLICATION_ID` | app.beehiiv.com → Settings (starts with pub_) |

---

### Step 4 — Update your affiliate tags in seed_products.json

Open `products/seed_products.json` and replace every `"REPLACE_WITH_YOUR_TAG"` with your
actual Amazon Associates tag (e.g., `"mysite-20"`).

---

### Step 5 — Update blog/_config.yml

```yaml
url: "https://unomedina93.github.io/deal-finder"
```

---

### Step 6 — Run it manually to test

```bash
cd ~/Desktop/affiliate-bot
cp .env.template .env
# Fill in .env with your real keys

pip install -r requirements.txt
cd bot
python main.py
```

The bot will generate content and print it to the console if GitHub/Buffer/Beehiiv
are not configured yet — so you can test the Claude output before going live.

---

### Step 7 — Push to GitHub

```bash
cd ~/Desktop/affiliate-bot
git init
git add .
git commit -m "Initial affiliate bot setup"
git remote add origin https://github.com/unomedina93/unomedina93.github.io/deal-finder.git
git push -u origin main
```

The GitHub Action will run automatically every day at 9 AM EST.
You can also trigger it manually: GitHub repo → Actions tab → "Daily Affiliate Content" → Run workflow.

---

## Adding More Products

Edit `products/seed_products.json` to add more products. Each product needs:
- `id` — unique string
- `name` — product name
- `niche` — `"home_decor"`, `"tools"`, or `"furniture"`
- `affiliate_network` — `"amazon"`, `"home_depot"`, or `"wayfair"`
- `product_url` — the product page URL
- `commission_rate` — as a decimal (e.g., `0.07` for 7%)
- `keywords` — list of 3-5 SEO keywords

---

## FTC Compliance

All generated content automatically includes:
- `#ad #affiliate` on every social post
- Disclosure quote at the top of every blog post
- Disclosure footer on every blog page
- Disclosure in every email section

This satisfies FTC requirements. Do not remove these disclosures.

---

## Monthly Cost

| Tool | Cost |
|------|------|
| Claude API (Haiku) | ~$0.05/month |
| GitHub | Free |
| Buffer | Free (3 channels) |
| Beehiiv | Free (up to 2,500 subs) |
| **Total** | **~$0.05/month** |

When you're ready to scale: upgrade Buffer ($6/mo) for unlimited posts, Beehiiv ($39/mo) for monetization features.
