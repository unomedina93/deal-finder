"""
Content Generator — powered by Groq (free tier)
Uses llama-3.3-70b-versatile: fast, high quality, 14,400 requests/day free.
Makes a SINGLE API call per product to minimize quota usage.
Returns: blog post, 5 pin descriptions, social caption, email section.
"""

import os
import time
from groq import Groq


client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL  = "llama-3.3-70b-versatile"


def _ask(prompt: str, retries: int = 3) -> str:
    """Send a prompt to Groq with retry on rate limit."""
    for attempt in range(retries):
        try:
            completion = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=4096,
                temperature=0.7,
            )
            return completion.choices[0].message.content
        except Exception as e:
            if "429" in str(e) and attempt < retries - 1:
                wait = 30 * (attempt + 1)
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

    keywords   = ", ".join(product.get("keywords", []))
    name       = product['name']
    brand      = product.get('brand', '')
    price      = product.get('price', '')
    desc       = product['description']
    niche      = product.get('niche', 'home')
    url        = product.get('affiliate_url', product['product_url'])

    prompt = f"""You are a helpful affiliate marketing content writer. Generate all of the following content for this product in a single response.

PRODUCT INFO:
- Name: {name}
- Brand: {brand}
- Price: ${price}
- Description: {desc}
- Keywords: {keywords}
- Niche: {niche}
- Affiliate URL: {url}

Generate the following 4 sections. Use the EXACT section headers shown below.

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
    """Parse the single combined response into 4 content pieces.
    Handles variations in how the model formats section headers.
    """
    import re

    def extract_section(text: str, header: str, next_header: str = None) -> str:
        # Match header in multiple formats: ---HEADER---, ### HEADER, ## HEADER, **HEADER**
        pattern = rf"(?:---\s*{re.escape(header)}\s*---|#+\s*{re.escape(header)}\s*|\*{{1,2}}{re.escape(header)}\*{{1,2}})"
        match = re.search(pattern, text, re.IGNORECASE)
        if not match:
            return ""
        start = match.end()
        if next_header:
            next_pattern = rf"(?:---\s*{re.escape(next_header)}\s*---|#+\s*{re.escape(next_header)}\s*|\*{{1,2}}{re.escape(next_header)}\*{{1,2}})"
            next_match = re.search(next_pattern, text[start:], re.IGNORECASE)
            if next_match:
                return text[start: start + next_match.start()].strip()
        return text[start:].strip()

    blog_post = extract_section(raw, "BLOG_POST",        "PIN_DESCRIPTIONS")
    pins_raw  = extract_section(raw, "PIN_DESCRIPTIONS",  "SOCIAL_CAPTION")
    social    = extract_section(raw, "SOCIAL_CAPTION",    "EMAIL_SECTION")
    email     = extract_section(raw, "EMAIL_SECTION")

    # Parse pin list — handle "1.", "1)" or just plain lines
    pin_lines    = [l.strip() for l in pins_raw.split("\n") if l.strip()]
    descriptions = []
    for line in pin_lines:
        match = re.match(r"^[\d]+[.)]\s*(.+)", line)
        if match:
            descriptions.append(match.group(1))
        elif line and not re.match(r"^[\d]+[.)]", line):
            descriptions.append(line)

    # Fallback: if parsing completely failed, print raw for debugging
    if not blog_post:
        print("WARNING: Could not parse blog post section. Raw response snippet:")
        print(raw[:500])

    return {
        "blog_post":        blog_post,
        "pin_descriptions": descriptions[:5],
        "social_caption":   social,
        "email_section":    email,
    }
