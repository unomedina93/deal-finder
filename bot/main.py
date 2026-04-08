"""
Affiliate Bot — Main Orchestrator
Runs the full pipeline daily:
  1. Pick a product
  2. Generate content with Claude
  3. Publish blog post to GitHub Pages
  4. Queue social posts to Buffer
  5. Queue email section to Beehiiv
  6. Log everything to logs/published.json
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load .env when running locally
load_dotenv(Path(__file__).parent.parent / ".env")

from product_discovery import pick_daily_product, get_recently_used_ids
from content_generator import generate_all_content
from publishers.blog_publisher import publish_blog_post
from publishers.buffer_publisher import schedule_social_posts
from publishers.beehiiv_publisher import queue_email_section


LOG_FILE = Path(__file__).parent.parent / "logs" / "published.json"


def run():
    print(f"\n{'='*60}")
    print(f"Affiliate Bot starting — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*60}\n")

    # 1. Pick product (rotate through all 3 niches evenly)
    niche       = _get_todays_niche()
    exclude_ids = get_recently_used_ids(LOG_FILE)
    product     = pick_daily_product(niche=niche, exclude_ids=exclude_ids)

    print(f"Today's product: {product['name']}")
    print(f"Niche: {niche} | Commission: {product['commission_rate']*100:.0f}%")
    print(f"Affiliate URL: {product['affiliate_url']}\n")

    # 2. Generate all content with Claude
    content = generate_all_content(product)

    # 3. Publish blog post
    blog_url = publish_blog_post(product, content["blog_post"])

    # 4. Queue social posts to Buffer
    buffer_ids = schedule_social_posts(
        product=product,
        pin_descriptions=content["pin_descriptions"],
        social_caption=content["social_caption"],
        blog_post_url=blog_url,
    )

    # 5. Queue email section to Beehiiv
    email_url = queue_email_section(product, content["email_section"])

    # 6. Log everything
    _log_run(product, blog_url, buffer_ids, email_url, content)

    print(f"\n{'='*60}")
    print(f"Done! Published: {product['name']}")
    print(f"Blog: {blog_url}")
    print(f"{'='*60}\n")


def _get_todays_niche() -> str:
    """Rotate through niches: Mon/Thu = tools, Tue/Fri = furniture, Wed/Sat/Sun = home_decor"""
    day = datetime.now().weekday()  # 0=Mon, 6=Sun
    rotation = {
        0: "tools",
        1: "furniture",
        2: "home_decor",
        3: "tools",
        4: "furniture",
        5: "home_decor",
        6: "home_decor",
    }
    return rotation[day]


def _log_run(product, blog_url, buffer_ids, email_url, content):
    """Append this run to the published log."""
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    existing = []
    if LOG_FILE.exists():
        with open(LOG_FILE) as f:
            existing = json.load(f)

    entry = {
        "date":          datetime.now().strftime("%Y-%m-%d"),
        "product_id":    product["id"],
        "product_name":  product["name"],
        "niche":         product.get("niche"),
        "commission":    product.get("commission_rate"),
        "affiliate_url": product.get("affiliate_url"),
        "blog_url":      blog_url,
        "buffer_ids":    buffer_ids,
        "email_url":     email_url,
    }
    existing.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)

    print(f"Logged to {LOG_FILE}")


if __name__ == "__main__":
    run()
