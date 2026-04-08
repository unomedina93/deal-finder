"""
Blog Publisher
Converts generated content into a Jekyll Markdown post and commits it
to your GitHub Pages repo via the GitHub API (no git needed locally).
"""

import os
import base64
import requests
from datetime import datetime
from pathlib import Path


GITHUB_TOKEN   = os.getenv("GITHUB_TOKEN")
GITHUB_REPO    = os.getenv("GITHUB_REPO")           # e.g. "yourusername/yourusername.github.io"
GITHUB_BRANCH  = os.getenv("GITHUB_BRANCH", "main")
GITHUB_API     = "https://api.github.com"


def publish_blog_post(product: dict, blog_post_markdown: str) -> str:
    """
    Creates a Jekyll post file and commits it to the GitHub Pages repo.
    Returns the live URL of the published post.
    """
    today       = datetime.now().strftime("%Y-%m-%d")
    slug        = _slugify(product["name"])
    filename    = f"blog/_posts/{today}-{slug}.md"
    front_matter = _build_front_matter(product, today)
    full_content = f"{front_matter}\n\n{blog_post_markdown}"

    _commit_file(filename, full_content, f"Add affiliate post: {product['name']}")

    repo_name = GITHUB_REPO.split("/")[-1] if GITHUB_REPO else "your-blog"
    username  = GITHUB_REPO.split("/")[0] if GITHUB_REPO else "yourusername"
    post_url  = f"https://{username}.github.io/{slug}/"

    print(f"Blog post published: {post_url}")
    return post_url


def _build_front_matter(product: dict, date: str) -> str:
    """Build Jekyll YAML front matter."""
    keywords = ", ".join(f'"{k}"' for k in product.get("keywords", [])[:5])
    return f"""---
layout: post
title: "{product['name']} — Honest Review & Best Price"
date: {date}
categories: [{product.get('niche', 'home')}]
tags: [{keywords}]
image: "{product.get('image_url', '')}"
affiliate_product: true
description: "{product['description'][:120]}..."
---"""


def _slugify(text: str) -> str:
    """Convert product name to URL-safe slug."""
    import re
    text = text.lower()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"\s+", "-", text.strip())
    return text[:60]


def _commit_file(path: str, content: str, message: str) -> None:
    """Commit a file to the GitHub repo via the API."""
    if not GITHUB_TOKEN or not GITHUB_REPO:
        # Save locally if GitHub not configured yet
        _save_locally(path, content)
        return

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    url = f"{GITHUB_API}/repos/{GITHUB_REPO}/contents/{path}"

    # Check if file already exists (get SHA for updates)
    sha = None
    check = requests.get(url, headers=headers)
    if check.status_code == 200:
        sha = check.json().get("sha")

    payload = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "branch": GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha

    response = requests.put(url, json=payload, headers=headers)
    response.raise_for_status()


def _save_locally(path: str, content: str) -> None:
    """Fallback: save the post file locally when GitHub is not configured."""
    local_path = Path(__file__).parent.parent.parent / path
    local_path.parent.mkdir(parents=True, exist_ok=True)
    local_path.write_text(content)
    print(f"Saved locally (GitHub not configured): {local_path}")
