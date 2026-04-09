"""
Buffer Publisher
Queues social media posts (Pinterest, Instagram, Facebook) via Buffer API.
Free tier: 3 channels, 10 scheduled posts.
"""

import os
import requests
from datetime import datetime, timedelta


BUFFER_TOKEN = os.getenv("BUFFER_ACCESS_TOKEN")
BUFFER_API   = "https://api.bufferapp.com/1"


def schedule_social_posts(
    product: dict,
    pin_descriptions: list[str],
    social_caption: str,
    blog_post_url: str,
) -> dict[str, str]:
    """
    Schedule posts to all configured Buffer channels.
    Returns a dict of channel_name -> Buffer post ID.
    """
    if not BUFFER_TOKEN:
        print("Buffer token not configured — printing posts to console instead.")
        _print_posts(product, pin_descriptions, social_caption, blog_post_url)
        return {}

    channel_ids = _get_channel_ids()
    results     = {}

    # Pinterest — use first pin description
    if "pinterest" in channel_ids:
        post_id = _create_buffer_post(
            profile_id=channel_ids["pinterest"],
            text=pin_descriptions[0],
            link=blog_post_url,
            image_url=product.get("image_url"),
        )
        results["pinterest"] = post_id

    # Instagram — use social caption
    if "instagram" in channel_ids:
        post_id = _create_buffer_post(
            profile_id=channel_ids["instagram"],
            text=social_caption,
            link=blog_post_url,
            image_url=product.get("image_url"),
        )
        results["instagram"] = post_id

    # Facebook — use social caption
    if "facebook" in channel_ids:
        post_id = _create_buffer_post(
            profile_id=channel_ids["facebook"],
            text=social_caption,
            link=blog_post_url,
            image_url=product.get("image_url"),
        )
        results["facebook"] = post_id

    print(f"Queued {len(results)} social posts to Buffer.")
    return results


def _get_channel_ids() -> dict[str, str]:
    """Fetch connected Buffer profiles and map by service name."""
    response = requests.get(
        f"{BUFFER_API}/profiles.json",
        params={"access_token": BUFFER_TOKEN}
    )
    if response.status_code != 200:
        print(f"Buffer API error: {response.text}")
        return {}

    profiles  = response.json()
    channel_map = {}
    for profile in profiles:
        service = profile.get("service", "").lower()
        channel_map[service] = profile["id"]

    return channel_map


def _create_buffer_post(
    profile_id: str,
    text: str,
    link: str,
    image_url: str = None,
) -> str:
    """Create a single Buffer post and return its ID."""
    payload = {
        "access_token": BUFFER_TOKEN,
        "profile_ids[]": profile_id,
        "text": text,
        "shorten": False,
        "now": False,   # Add to Buffer queue (scheduled at optimal time)
    }

    if link:
        payload["media[link]"] = link

    if image_url:
        payload["media[photo]"] = image_url

    response = requests.post(f"{BUFFER_API}/updates/create.json", data=payload)
    if response.status_code == 200:
        return response.json().get("updates", [{}])[0].get("id", "")
    else:
        print(f"Buffer post failed: {response.text}")
        return ""


def _print_posts(product, pin_descriptions, social_caption, blog_post_url):
    """Print posts to console when Buffer is not configured (useful for testing)."""
    print("\n" + "="*60)
    print("PINTEREST POST (copy to Pinterest manually):")
    print("="*60)
    print(pin_descriptions[0] if pin_descriptions else "(no pin descriptions generated)")
    print(f"\nLink: {blog_post_url}")
    print(f"Image: {product.get('image_url', 'N/A')}")

    print("\n" + "="*60)
    print("INSTAGRAM / FACEBOOK POST:")
    print("="*60)
    print(social_caption)
    print(f"\nLink: {blog_post_url}")
    print("="*60 + "\n")
