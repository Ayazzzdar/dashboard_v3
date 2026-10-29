"""
Shopify helpers for the Memorial pack.

Memorial orders come from the product "The Day You Passed Archive"
(handle: the-day-you-passed-archive, id 9437528588443). Its theme snippet
`tdp-fields.liquid` sends three line-item properties:

    Full Name
    Date of Birth        DD/MM/YYYY
    Date of Passing      DD/MM/YYYY

This module fetches unfulfilled orders and extracts the memorial line items.
Kept separate from dashboard_v3.py (a Streamlit script, not import-safe).
"""

import re
import time
import requests

MEMORIAL_PRODUCT_ID = 9437528588443
MEMORIAL_TITLE_HINT = "day you passed"

API_VERSION = "2024-01"
FIELDS = "id,name,email,line_items,fulfillment_status,created_at,shipping_lines"


def _get(base, headers, params, timeout=30, max_retries=6):
    """GET with Shopify rate-limit (429) handling: honour Retry-After and back off."""
    delay = 1.0
    for _ in range(max_retries):
        r = requests.get(base, headers=headers, params=params, timeout=timeout)
        if r.status_code == 429:
            wait = r.headers.get("Retry-After")
            try:
                wait = float(wait) if wait else delay
            except ValueError:
                wait = delay
            time.sleep(min(wait, 5.0))
            delay = min(delay * 2, 5.0)
            continue
        return r
    return r  # last response (still 429) — caller raises


def fetch_unfulfilled_orders(token, store, include_fulfilled=False):
    """Fetch memorial-eligible orders (cursor pagination; filters only on page 1,
    the same fix as the main dashboard).

    By default only UNFULFILLED orders are returned. Pass include_fulfilled=True
    to return every order (any fulfilment status) — useful for regenerating a
    pack for an order that has already been fulfilled."""
    base = f"https://{store}/admin/api/{API_VERSION}/orders.json"
    headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    all_orders, page_info = [], None
    while True:
        if page_info:
            params = {"limit": 250, "fields": FIELDS, "page_info": page_info}
        else:
            params = {"status": "any", "limit": 250, "fields": FIELDS}
            if not include_fulfilled:
                params["fulfillment_status"] = "unfulfilled"
        r = _get(base, headers, params, timeout=30)
        if r.status_code != 200:
            raise RuntimeError(f"Shopify API {r.status_code}: {r.text[:200]}")
        all_orders.extend(r.json().get("orders", []))
        link = r.headers.get("Link", "")
        if 'rel="next"' in link:
            m = re.search(r"page_info=([^&>]+)", link)
            page_info = m.group(1) if m else None
            if not page_info:
                break
            time.sleep(0.6)  # stay under Shopify's 2 req/sec REST limit
        else:
            break
    return all_orders


def fetch_order_by_name(token, store, order_number):
    """Fetch a single order by its number/name (e.g. '4663' or '#4663') in one
    API call — no scanning, so it works regardless of fulfilment status and never
    hits the rate limit. Returns a list (0 or 1 orders)."""
    name = str(order_number).strip()
    if not name:
        return []
    hashed = name if name.startswith("#") else f"#{name}"
    base = f"https://{store}/admin/api/{API_VERSION}/orders.json"
    headers = {"X-Shopify-Access-Token": token, "Content-Type": "application/json"}
    params = {"status": "any", "name": hashed, "limit": 50, "fields": FIELDS}
    r = _get(base, headers, params, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"Shopify API {r.status_code}: {r.text[:200]}")
    orders = r.json().get("orders", [])
    # Keep only the exact order. The name filter can match partially
    # (#466 -> #4663, #46630); and if the filter were ever ignored it would
    # return recent orders, so matching exactly avoids loading the wrong order.
    want = hashed.lstrip("#")
    return [o for o in orders if o.get("name", "").lstrip("#") == want]


def _is_express(order):
    for line in order.get("shipping_lines", []) or []:
        if "express" in f"{line.get('title', '')} {line.get('code', '')}".lower():
            return True
    return False


def _is_memorial_item(line_item):
    if line_item.get("product_id") == MEMORIAL_PRODUCT_ID:
        return True
    return MEMORIAL_TITLE_HINT in (line_item.get("title") or "").lower()


def _quantity(line_item):
    """Copies ordered of this line item (customers are prompted to buy multiple
    copies). Defaults to 1 if missing/unparseable."""
    try:
        q = int(line_item.get("quantity") or 1)
        return q if q > 0 else 1
    except (TypeError, ValueError):
        return 1


def extract_memorial_orders(orders):
    """Return one record per memorial line item:
    {order_name, item_index, multi, item_count, name, dob, dop, express, quantity}."""
    out = []
    for o in orders:
        lis = o.get("line_items", [])
        mem_idx = [i for i, li in enumerate(lis) if _is_memorial_item(li)]
        express = _is_express(o)
        for i in mem_idx:
            props = {p.get("name"): (p.get("value") or "")
                     for p in (lis[i].get("properties") or [])}
            out.append({
                "order_name": o.get("name", ""),
                "item_index": i,
                "multi": len(mem_idx) > 1,
                "item_count": len(mem_idx),
                "name": (props.get("Full Name") or "").strip(),
                "dob": (props.get("Date of Birth") or "").strip(),
                "dop": (props.get("Date of Passing") or "").strip(),
                "express": express,
                "quantity": _quantity(lis[i]),
            })
    return out
