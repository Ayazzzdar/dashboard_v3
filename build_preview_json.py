"""
Build the storefront preview dataset for The Day Archive product page.

Reads the verified lookup CSVs in data/ and emits a single compact JSON file
that the Shopify theme ships as an asset, so the "see your date before you
buy" preview needs no API, no server and no LLM call.

Only the DETERMINISTIC, CSV-backed fields go in here. The generated narrative
copy on the printed pages is deliberately excluded: if the preview ever
disagreed with the posted pack, the preview would become a liability.

Usage:
    python build_preview_json.py                 # writes tda-preview.json
    python build_preview_json.py out/preview.json

Then upload the result to the theme as assets/tda-preview.json.
"""

import csv
import json
import sys
from datetime import date
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# year-keyed tables -> (filename, value column, key in the output)
YEAR_TABLES = [
    ("number1_songs.csv", "number1_song", "song"),
    ("average_house.csv", "average_house", "house"),
    ("average_salary.csv", "average_annual_salary", "salary"),
    ("petrol_prices.csv", "petrol_price", "petrol"),
    ("afl_winners.csv", "winner", "afl"),
    ("nrl_winners.csv", "winner", "nrl"),
]

# date-range tables -> (filename, output key)
RANGE_TABLES = [
    ("pm_terms.csv", "pm"),
    ("monarchs.csv", "monarch"),
]


def load_year_table(filename, value_col, out_key, years):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"  ! missing {filename}, skipped")
        return 0
    n = 0
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            try:
                year = int(row["year"])
            except (KeyError, ValueError):
                continue
            value = (row.get(value_col) or "").strip()
            if not value:
                continue
            years.setdefault(str(year), {})[out_key] = value
            n += 1
    return n


def load_range_table(filename):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"  ! missing {filename}, skipped")
        return []
    out = []
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            start = (row.get("start_date") or "").strip()
            end = (row.get("end_date") or "").strip()
            name = (row.get("name") or "").strip()
            if not (start and end and name):
                continue
            out.append([start, end, name])
    out.sort(key=lambda r: r[0])
    return out


def main():
    out_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("tda-preview.json")

    years = {}
    print("year tables:")
    for filename, value_col, out_key in YEAR_TABLES:
        n = load_year_table(filename, value_col, out_key, years)
        print(f"  {filename:24s} -> {out_key:8s} {n} rows")

    ranges = {}
    print("range tables:")
    for filename, out_key in RANGE_TABLES:
        rows = load_range_table(filename)
        ranges[out_key] = rows
        print(f"  {filename:24s} -> {out_key:8s} {len(rows)} ranges")

    known = sorted(int(y) for y in years)
    payload = {
        "generated": date.today().isoformat(),
        "minYear": known[0] if known else None,
        "maxYear": known[-1] if known else None,
        "years": years,
        "ranges": ranges,
    }

    # Compact values, but one line per year so the asset stays diffable in git
    # and reviewable by eye. Costs ~160 bytes against an 18KB file.
    def row(obj):
        return json.dumps(obj, separators=(",", ":"), ensure_ascii=False)

    lines = ["{"]
    lines.append('"generated":%s,' % row(payload["generated"]))
    lines.append('"minYear":%s,' % row(payload["minYear"]))
    lines.append('"maxYear":%s,' % row(payload["maxYear"]))
    lines.append('"years":{')
    year_keys = sorted(years, key=int)
    for i, y in enumerate(year_keys):
        comma = "" if i == len(year_keys) - 1 else ","
        lines.append('%s:%s%s' % (row(y), row(years[y]), comma))
    lines.append("},")
    lines.append('"ranges":{')
    range_keys = list(ranges)
    for i, k in enumerate(range_keys):
        comma = "" if i == len(range_keys) - 1 else ","
        lines.append('%s:%s%s' % (row(k), row(ranges[k]), comma))
    lines.append("}")
    lines.append("}")

    text = "\n".join(lines) + "\n"
    json.loads(text)  # fail loudly here rather than in a browser
    out_path.write_text(text, encoding="utf-8")

    print(f"\nwrote {out_path} - {len(text.encode('utf-8'))} bytes, "
          f"{len(years)} years ({payload['minYear']}-{payload['maxYear']})")


if __name__ == "__main__":
    main()
