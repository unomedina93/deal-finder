"""
Content Generator — powered by Google Gemini (free tier)
Uses the new google-genai SDK with gemini-2.0-flash-lite (free, fast)
Generates all content for one product:
  - SEO blog post (Markdown)
  - 5 Pinterest pin descriptions
  - Instagram/Facebook caption
  - Email newsletter section
"""

import os
from google import genai


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL  = "gemini-2.0-flash-lite"  # Free tier, fast, great quality


def _ask(prompt: str) -> str:
    """Send a prompt to Gemini and return the text response."""
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


def generate_all_content(product: dict) -> dict:
    """
    Generate all content for a product.
    Returns a dict with keys: blog_post, pin_descriptions, social_caption, email_section
    """
    print(f"Generating content for: {product['name']}")

    return {
        "blog_post":        generate_blog_post(product),
        "pin_descriptions": generate_pin_descriptions(product),
        "social_caption":   generate_social_caption(product),
        "email_section":    generate_email_section(product),
    }


def generate_blog_post(product: dict) -> str:
    """Generate a 900-1100 word SEO-optimized blog post in Markdown."""
    keywords = ", ".join(product.get("keywords", []))
    prompt = f"""Write a helpful, SEO-optimized blog post about this product.

Product: {product['name']}
Brand: {product.get('brand', '')}
Price: ${product.get('price', '')}
Description: {product['description']}
Target keywords: {keywords}
Niche: {product.get('niche', 'home')}
Affiliate URL: {product.get('affiliate_url', product['product_url'])}

Requirements:
- Length: 900-1100 words
- Format: Markdown with H2 and H3 subheadings
- Tone: Helpful, honest, conversational — like a knowledgeable friend
- Structure: Intro → Key features → Who it's for → Pros & cons → Final verdict
- Include the primary keyword naturally in the title, first paragraph, and 2-3 subheadings
- Add a clear call-to-action with the affiliate URL near the end
- Include this FTC disclosure at the very top (before the title):
  > *This post contains affiliate links. I may earn a commission at no extra cost to you.*
- Do NOT start the title with "Verify"
- Do NOT use phrases like "game changer" or "life changing"
- End with a brief FAQ section (3 questions)

Write only the blog post content. No meta commentary."""

    return _ask(prompt)


def generate_pin_descriptions(product: dict) -> list[str]:
    """Generate 5 Pinterest pin descriptions (SEO-optimized, disclosure included)."""
    keywords = ", ".join(product.get("keywords", [])[:3])
    prompt = f"""Write 5 Pinterest pin descriptions for this product.

Product: {product['name']}
Price: ${product.get('price', '')}
Description: {product['description']}
Affiliate URL: {product.get('affiliate_url', product['product_url'])}
Keywords to include: {keywords}

Requirements for EACH description:
- Length: 150-200 characters (Pinterest sweet spot)
- Include 1-2 of the target keywords naturally
- Include the price to boost click-through rate
- Include a call to action (Shop now, See price, Get it here, etc.)
- End with: #ad #affiliate
- Each description should have a different angle:
  1. Feature-focused
  2. Problem/solution focused
  3. Value/price focused
  4. Lifestyle/aspirational
  5. Gift idea angle

Format your response as a numbered list (1. 2. 3. 4. 5.) with just the description text."""

    raw = _ask(prompt)
    lines = [line.strip() for line in raw.split("\n") if line.strip()]
    descriptions = []
    for line in lines:
        if line and line[0].isdigit() and ". " in line:
            descriptions.append(line.split(". ", 1)[1])
        elif line and not line[0].isdigit():
            descriptions.append(line)
    return descriptions[:5]


def generate_social_caption(product: dict) -> str:
    """Generate an Instagram/Facebook caption with disclosure."""
    prompt = f"""Write a short, engaging Instagram and Facebook caption for this product.

Product: {product['name']}
Price: ${product.get('price', '')}
Description: {product['description']}
Affiliate URL: {product.get('affiliate_url', product['product_url'])}

Requirements:
- Length: 2-3 sentences max
- Hook in the first line (no "I" as the first word)
- Conversational, not salesy
- Include the price
- End with: Link in bio! #ad #affiliate
- Add 5-8 relevant hashtags on a new line at the end

Write only the caption. No meta commentary."""

    return _ask(prompt)


def generate_email_section(product: dict) -> str:
    """Generate a short email newsletter section (HTML-friendly Markdown)."""
    prompt = f"""Write a short product spotlight section for a weekly email newsletter.

Product: {product['name']}
Price: ${product.get('price', '')}
Description: {product['description']}
Affiliate URL: {product.get('affiliate_url', product['product_url'])}

Requirements:
- Length: 80-120 words
- Friendly, personal tone — like a tip from a friend
- One clear benefit stated upfront
- Include the price
- One CTA link using this format: [Shop {product['name']} → affiliate URL]
- Include this disclosure on the last line: *Affiliate link — I earn a small commission at no extra cost to you.*

Write only the section content. No subject line. No meta commentary."""

    return _ask(prompt)
