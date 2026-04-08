"""
Content Generator — powered by Google Gemini (free tier)
Makes a SINGLE API call per product to minimize quota usage.
Returns: blog post, 5 pin descriptions, social caption, email section.
"""

import os
import json
import time
from google import genai


client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL  = "gemini-2.0-flash-lite"


def _ask(prompt: str, retries: int = 3) -> str:
    """Send a prompt to Gemini with retry on rate limit."""
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model=MODEL, contents=prompt)
            return response.text
        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                wait = 30 * (attempt + 1)  # 30s, 60s, 90s
                print(f"Rate limited — waiting {wait}s before retry {attempt + 2}/{retries}")
                time.sleep(wait)
            else:
                raise
    return ""


def generate_all_content(product: dict) -> dict:
    """
    Generate ALL content in a single API call to minimize quota usage.
    Returns a dict with keys: blog_post, pin_descriptions, social_caption, email_section
    """
    print(f"Generating content for: {product['name']}")

    keywords    = ", ".join(product.get("keywords", []))
    keywords_3  = ", ".join(product.get("keywords", [])[:3])
    name        = product['name']
    brand       = product.get('brand', '')
    price       = product.get('price', '')
    description = product['description']
    niche       = product.get('niche', 'home')
    url         = product.get('affiliate_url', product['product_url'])

    prompt = f"""You are a helpful affiliate marketing content writer. Generate all of the following content for this product in a single response.

PRODUCT INFO:
- Name: {name}
- Brand: {brand}
- Price: ${price}
- Description: {description}
- Keywords: {keywords}
- Niche: {niche}
- Affiliate URL: {url}

Generate the following 4 sections. Use the EXACT section headers shown below so the content can be parsed.

---BLOG_POST---
Write a 900-1100 word SEO-optimized blog post in Markdown.
- Include H2 and H3 subheadings
- Tone: helpful, honest, conversational
- Structure: Intro → Key features → Who it's for → Pros & cons → Final verdict → FAQ (3 questions)
- Primary keyword in title, first paragraph, and 2-3 subheadings
- Call-to-action with the affiliate URL near the end
- FTC disclosure at the very top: > *This post contains affiliate links. I may earn a commission at no extra cost to you.*
- Do NOT use "game changer" or "life changing"

---PIN_DESCRIPTIONS---
Write 5 Pinterest pin descriptions as a numbered list (1. 2. 3. 4. 5.)
Each description:
- 150-200 characters
- Includes 1-2 keywords naturally
- Includes the price
- Ends with: #ad #affiliate
- Different angles: 1) Feature-focused 2) Problem/solution 3) Value/price 4) Lifestyle 5) Gift idea

---SOCIAL_CAPTION---
Write one Instagram/Facebook caption.
- 2-3 sentences max
- Hook first line (no "I" as first word)
- Include the price
- End with: Link in bio! #ad #affiliate
- 5-8 hashtags on a new line

---EMAIL_SECTION---
Write an 80-120 word product spotlight for a weekly email newsletter.
- Friendly, personal tone
- One clear benefit upfront
- Include the price
- CTA: [Shop {name} → {url}]
- Last line: *Affiliate link — I earn a small commission at no extra cost to you.*"""

    raw = _ask(prompt)
    return _parse_response(raw)


def _parse_response(raw: str) -> dict:
    """Parse the single combined Gemini response into 4 content pieces."""

    def extract_section(text: str, header: str, next_header: str = None) -> str:
        start = text.find(f"---{header}---")
        if start == -1:
            return ""
        start += len(f"---{header}---")
        if next_header:
            end = text.find(f"---{next_header}---", start)
            return text[start:end].strip() if end != -1 else text[start:].strip()
        return text[start:].strip()

    blog_post    = extract_section(raw, "BLOG_POST",      "PIN_DESCRIPTIONS")
    pins_raw     = extract_section(raw, "PIN_DESCRIPTIONS", "SOCIAL_CAPTION")
    social       = extract_section(raw, "SOCIAL_CAPTION",  "EMAIL_SECTION")
    email        = extract_section(raw, "EMAIL_SECTION")

    # Parse pin descriptions into a list
    pin_lines    = [l.strip() for l in pins_raw.split("\n") if l.strip()]
    descriptions = []
    for line in pin_lines:
        if line and line[0].isdigit() and ". " in line:
            descriptions.append(line.split(". ", 1)[1])
    if not descriptions:
        descriptions = [l for l in pin_lines if l]
    descriptions = descriptions[:5]

    return {
        "blog_post":        blog_post,
        "pin_descriptions": descriptions,
        "social_caption":   social,
        "email_section":    email,
    }
