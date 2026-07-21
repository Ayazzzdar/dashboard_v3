"""
The Day Archive - render pipeline orchestrator.

Produces the 5-page personalised birthday pack as transparent PNGs,
one file per page, from an order dict or a CSV export.

Filename convention (Option B):
    "{OrderID} - {Name} - {page}.png"
  e.g. "#2024 - MALCOLM BURROWS - 1.png"
       "#2025 (Item 1 of 2) - LYN LIPMAN - 3.png"

The "(Item x/y)" marker is preserved (with "/" -> " of ") so the packs
that belong to the same Shopify order stay identifiable and never collide.

Usage:
    from render_pack import render_pack, render_from_csv

    # single order (dict with the CSV column names as keys)
    paths = render_pack(order, "output/packs")

    # whole CSV export
    all_paths = render_from_csv("1996_-_2025.csv", "output/packs")
"""

import os
import re
import csv as _csv

from page1_overview import render_page1
from page2_archive import render_page2
from page3_economy import render_page3
from page4_culture import render_page4
from page5_names import render_page5

PAGE_RENDERERS = [render_page1, render_page2, render_page3, render_page4, render_page5]

_ILLEGAL = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def build_filename(order_id, name, page):
    """Build a safe PNG filename following the Option B convention."""
    oid = (order_id or "").strip()
    # convert "(Item 1/2)" -> "(Item 1 of 2)" so the slash is filesystem-safe
    oid = re.sub(r"\(Item\s*(\d+)\s*/\s*(\d+)\)", r"(Item \1 of \2)", oid)
    nm = (name or "").strip()
    base = f"{oid} - {nm} - {page}"
    # strip any remaining characters that are illegal in filenames
    base = _ILLEGAL.sub("", base).strip()
    return f"{base}.png"


def render_pack(order, output_dir):
    """
    Render all 5 pages for a single order as transparent PNGs.

    `order` is a dict keyed by the CSV column names (OrderID, Name,
    AverageSalary, BoyName1, ...). Returns the list of 5 output paths.
    """
    os.makedirs(output_dir, exist_ok=True)
    order_id = order.get("OrderID", "")
    name = order.get("Name", "")

    paths = []
    for page_num, renderer in enumerate(PAGE_RENDERERS, start=1):
        fname = build_filename(order_id, name, page_num)
        out_path = os.path.join(output_dir, fname)
        renderer(order, out_path)
        paths.append(out_path)
    return paths


def render_from_csv(csv_path, output_dir, limit=None, on_progress=None):
    """
    Render packs for every row in a CSV export.

    - limit: optionally cap how many orders to render (for testing).
    - on_progress: optional callback(index, total, name, paths) for UI
      progress (e.g. a Streamlit progress bar).

    Returns a dict: {OrderID+Name: [5 paths]} for every order rendered.
    """
    with open(csv_path, encoding="utf-8", errors="replace") as f:
        rows = list(_csv.DictReader(f))
    if limit:
        rows = rows[:limit]

    results = {}
    total = len(rows)
    for i, order in enumerate(rows, start=1):
        paths = render_pack(order, output_dir)
        key = f"{order.get('OrderID', '')} - {order.get('Name', '')}"
        results[key] = paths
        if on_progress:
            on_progress(i, total, order.get("Name", ""), paths)
    return results


if __name__ == "__main__":
    import sys
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "1996_-_2025.csv"
    out_dir = sys.argv[2] if len(sys.argv) > 2 else "output/packs"
    lim = int(sys.argv[3]) if len(sys.argv) > 3 else None

    def _prog(i, total, name, paths):
        print(f"[{i}/{total}] {name}: {len(paths)} pages")

    res = render_from_csv(csv_path, out_dir, limit=lim, on_progress=_prog)
    print(f"\nDone. Rendered {len(res)} packs ({len(res) * 5} PNGs) into {out_dir}/")
