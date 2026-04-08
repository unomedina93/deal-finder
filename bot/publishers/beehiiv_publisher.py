"""
Beehiiv Publisher
Queues a product spotlight section to your Beehiiv newsletter as a draft.
Free tier: up to 2,500 subscribers.
"""

import os
import requests


BEEHIIV_API_KEY  = os.getenv("BEEHIIV_API_KEY")
BEEHIIV_PUB_ID   = os.getenv("BEEHIIV_PUBLICATION_ID")
BEEHIIV_API      = "https://api.beehiiv.com/v2"


def queue_email_section(product: dict, email_section_markdown: str) -> str:
    """
    Creates a draft post in Beehiiv with the product spotlight section.
    Returns the draft post URL.
    """
    if not BEEHIIV_API_KEY or not BEEHIIV_PUB_ID:
        print("Beehiiv not configured — printing email section to console instead.")
        _print_email_section(product, email_section_markdown)
        return ""

    html_content = _markdown_to_simple_html(email_section_markdown)

    payload = {
        "publication_id": BEEHIIV_PUB_ID,
        "subject":        f"This Week's Pick: {product['name']}",
        "subtitle":       product["description"][:100],
        "content_html":   html_content,
        "status":         "draft",    # Always draft first — you review before sending
        "authors":        [],
    }

    headers = {
        "Authorization": f"Bearer {BEEHIIV_API_KEY}",
        "Content-Type":  "application/json",
    }

    response = requests.post(
        f"{BEEHIIV_API}/publications/{BEEHIIV_PUB_ID}/posts",
        json=payload,
        headers=headers,
    )

    if response.status_code in (200, 201):
        post_id  = response.json().get("data", {}).get("id", "")
        post_url = f"https://app.beehiiv.com/posts/{post_id}"
        print(f"Email draft created in Beehiiv: {post_url}")
        return post_url
    else:
        print(f"Beehiiv API error: {response.status_code} — {response.text}")
        return ""


def _markdown_to_simple_html(markdown: str) -> str:
    """Convert basic Markdown to HTML for Beehiiv (no extra dependencies)."""
    import re

    html = markdown

    # Bold
    html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
    # Italic / disclosure
    html = re.sub(r"\*(.+?)\*", r"<em>\1</em>", html)
    # Links [text](url)
    html = re.sub(r"\[(.+?)\]\((.+?)\)", r'<a href="\2">\1</a>', html)
    # Paragraph breaks
    paragraphs = [f"<p>{p.strip()}</p>" for p in html.split("\n\n") if p.strip()]
    return "\n".join(paragraphs)


def _print_email_section(product: dict, email_section_markdown: str) -> None:
    """Print email section to console when Beehiiv is not configured."""
    print("\n" + "="*60)
    print("EMAIL NEWSLETTER SECTION (copy to Beehiiv manually):")
    print("="*60)
    print(email_section_markdown)
    print("="*60 + "\n")
