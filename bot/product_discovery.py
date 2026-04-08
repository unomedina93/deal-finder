"""
Product Discovery Module
Phase 1: Reads from seed_products.json (no API needed to start)
Phase 2: Amazon PA-API (uncomment when Associates account is active)
"""

import json
import os
import random
from pathlib import Path


PRODUCTS_FILE = Path(__file__).parent.parent / "products" / "seed_products.json"


def load_seed_products(niche: str = None) -> list[dict]:
    """Load products from the local seed JSON file."""
    with open(PRODUCTS_FILE) as f:
        products = json.load(f)

    if niche:
        products = [p for p in products if p.get("niche") == niche]

    return products


def pick_daily_product(niche: str = None, exclude_ids: list[str] = None) -> dict:
    """
    Pick one product to feature today.
    Rotates through all products before repeating.
    Optionally filter by niche: 'home_decor', 'tools', 'furniture'
    """
    products = load_seed_products(niche)

    if exclude_ids:
        products = [p for p in products if p["id"] not in exclude_ids]

    if not products:
        # All products used recently — reset rotation
        products = load_seed_products(niche)

    # Prioritize higher commission products (weighted random)
    weights = [p.get("commission_rate", 0.05) for p in products]
    product = random.choices(products, weights=weights, k=1)[0]

    # Build affiliate URL
    product["affiliate_url"] = _build_affiliate_url(product)

    return product


def _build_affiliate_url(product: dict) -> str:
    """Generate the affiliate tracking URL for a product."""
    network = product.get("affiliate_network", "amazon")
    tag = os.getenv("AMAZON_ASSOCIATE_TAG", product.get("affiliate_tag", ""))

    if network == "amazon":
        asin = product.get("asin", "")
        return f"https://www.amazon.com/dp/{asin}?tag={tag}"

    elif network == "home_depot":
        base_url = product.get("product_url", "")
        hd_tag = os.getenv("HOME_DEPOT_AFFILIATE_TAG", "")
        return f"{base_url}?cm_mmc=afl-ir-{hd_tag}"

    elif network == "wayfair":
        base_url = product.get("product_url", "")
        wf_tag = os.getenv("WAYFAIR_AFFILIATE_TAG", "")
        return f"{base_url}?refid={wf_tag}"

    return product.get("product_url", "")


def get_recently_used_ids(log_file: Path = None) -> list[str]:
    """Read the last 7 days of published product IDs to avoid repeats."""
    if log_file is None:
        log_file = Path(__file__).parent.parent / "logs" / "published.json"

    if not log_file.exists():
        return []

    with open(log_file) as f:
        log = json.load(f)

    # Return IDs from the last 7 entries
    return [entry["product_id"] for entry in log[-7:]]


# --- Phase 2: Amazon PA-API (activate when Associates account is approved) ---
# Uncomment and install: pip install amazon-paapi5
#
# from paapi5_python_sdk.api.default_api import DefaultApi
# from paapi5_python_sdk.models.partner_type import PartnerType
# from paapi5_python_sdk.models.search_items_request import SearchItemsRequest
#
# def search_amazon_products(keywords: str, category: str = "HomeGarden") -> list[dict]:
#     api = DefaultApi(
#         access_key=os.getenv("AMAZON_ACCESS_KEY"),
#         secret_key=os.getenv("AMAZON_SECRET_KEY"),
#         host="webservices.amazon.com",
#         region="us-east-1"
#     )
#     request = SearchItemsRequest(
#         partner_tag=os.getenv("AMAZON_ASSOCIATE_TAG"),
#         partner_type=PartnerType.ASSOCIATES,
#         keywords=keywords,
#         search_index=category,
#         item_count=10,
#         resources=["ItemInfo.Title", "Offers.Listings.Price", "Images.Primary.Large"]
#     )
#     response = api.search_items(request)
#     return _parse_amazon_response(response)
