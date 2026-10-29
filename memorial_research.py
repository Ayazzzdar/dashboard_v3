"""
Memorial pack research + data assembly.

Given a name, date of birth and date of passing, this:
  1. Computes everything derivable from the two dates (lifespan, age, the
     birth-month flower, and the "Life in Numbers" figures) — no AI needed.
  2. Researches the world on the DATE OF PASSING via the Claude API: people who
     died that day ("Remembered on this day"), on-this-day events, and the
     death-year's PM/monarch/sport/songs/prices/culture.
  3. Overrides the verifiable facts with the repo's own lookup tables where they
     have an entry (same accuracy approach as the birthday pack).
  4. Returns a flat token dict ready for memorial_render.render_memorial_pack().

Self-contained: imports only lookup_tables (dashboard_v3.py is a Streamlit
script and is not import-safe).
"""

import os
import re
import json
import html
import datetime

import requests

import lookup_tables as LT

_HERE = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(_HERE, "memorial", "assets")

CLAUDE_MODEL = "claude-sonnet-4-6"
CLAUDE_URL = "https://api.anthropic.com/v1/messages"

# Birth-month flower (name, asset filename). Falls back to daffodil until the
# other engravings are added to memorial/assets/.
MONTH_FLOWERS = {
    1: ("Carnation", "carnation.png"), 2: ("Violet", "violet.png"),
    3: ("Daffodil", "daffodil.png"), 4: ("Daisy", "daisy.png"),
    5: ("Lily of the Valley", "lily_of_the_valley.png"), 6: ("Rose", "rose.png"),
    7: ("Larkspur", "larkspur.png"), 8: ("Gladiolus", "gladiolus.png"),
    9: ("Aster", "aster.png"), 10: ("Marigold", "marigold.png"),
    11: ("Chrysanthemum", "chrysanthemum.png"), 12: ("Narcissus", "narcissus.png"),
}

MONTHS = ["", "January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December"]


# ----------------------------------------------------------------------------
# date / number helpers
# ----------------------------------------------------------------------------
def parse_date(s):
    """Accept DD/MM/YYYY or YYYY-MM-DD."""
    s = str(s).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d.%m.%Y"):
        try:
            return datetime.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognised date: {s!r} (use DD/MM/YYYY)")


def ordinal(n):
    if 10 <= n % 100 <= 20:
        suf = "th"
    else:
        suf = {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return suf


def esc(s):
    return html.escape(str(s or ""), quote=False)


def commaize(s):
    """Add thousands separators to any run of 4+ digits (e.g. $78000 -> $78,000)."""
    if not s:
        return s
    return re.sub(r"\d{4,}", lambda m: f"{int(m.group()):,}", str(s))


def life_numbers(dob, dop):
    days = (dop - dob).days
    years = dop.year - dob.year - ((dop.month, dop.day) < (dob.month, dob.day))
    weeks = days // 7
    moons = round(days / 29.53059)
    beats = days * 24 * 60 * 72
    return {
        "days": f"{days:,}", "years": years, "weeks": f"{weeks:,}",
        "moons": f"{moons:,}", "heartbeats": f"{beats / 1e9:.1f}",
    }


def birth_flower(month):
    name, fname = MONTH_FLOWERS.get(month, ("Daffodil", "daffodil.png"))
    warning = None
    if not os.path.exists(os.path.join(ASSETS_DIR, fname)):
        warning = (f"Flower asset '{fname}' for {name} is missing — using Daffodil. "
                   f"Add memorial/assets/{fname} to show the correct birth-month flower.")
        name, fname = "Daffodil", "daffodil.png"
    return name, fname, warning


# ----------------------------------------------------------------------------
# unknown / future-data normaliser (keeps placeholders short, no "cutoff" text)
# ----------------------------------------------------------------------------
_CUTOFF = re.compile(
    r"[\s\-–—:;,]*(?:(?:as of|outside|beyond|past|after|based on)?\s*(?:my |the |its )?"
    r"(?:knowledge|training(?:\s+data)?)\s*cut[\s\-]?off|not yet (?:determined|announced|decided|known|available)"
    r"|as of my last (?:update|training)).*$", re.IGNORECASE)


def _clean(v):
    if not isinstance(v, str):
        return v
    out = _CUTOFF.sub("", v)
    out = re.sub(r"[\s\-–—:;,]+$", "", out).strip()
    return out or "Unknown"


# ----------------------------------------------------------------------------
# Claude research (keyed to the DATE OF PASSING)
# ----------------------------------------------------------------------------
def _prompt(month_name, day, year):
    return f"""You are a historical research expert. Research accurate data about the world on {month_name} {day}, {year} (Australia), for a tasteful memorial keepsake. Accuracy matters more than speed.

Return ONLY valid JSON (no markdown), exactly this structure:

{{
  "Remembered": [
    {{"name": "Full name of a NOTABLE person who DIED on {month_name} {day} (ANY year) — verify the DEATH date", "role": "2-3 word role, e.g. 'Singer', 'Prime Minister'"}},
    {{"name": "A second notable person who DIED on {month_name} {day}", "role": "..."}},
    {{"name": "A third notable person who DIED on {month_name} {day}", "role": "..."}}
  ],
  "News": [
    "A notable world event that happened on {month_name} {day} (any year). ONE sentence, MAX 18 WORDS. Vary the eras. NOT all about deaths.",
    "A second, different on-this-day event. MAX 18 WORDS.",
    "A third, different on-this-day event. MAX 18 WORDS."
  ],
  "Historical": [
    {{"year": "1800s year", "text": "ONE COMPLETE SENTENCE (20-30 words) describing a major event that happened on {month_name} {day} in the 1800s. Include key details — who, what, where, and why it mattered. Example: 'On April 10, 1849, American inventor Walter Hunt patented the modern safety pin, a simple device he reportedly designed in three hours to settle a $15 debt.'"}},
    {{"year": "early-1900s year", "text": "ONE COMPLETE SENTENCE (20-30 words) describing a major event on {month_name} {day} (1900-1945). Include who was involved, what happened, where, and its significance."}},
    {{"year": "mid-1900s year", "text": "ONE COMPLETE SENTENCE (20-30 words) describing a major event on {month_name} {day} (1946-1999). Include who was involved, what happened, where, and why it mattered."}},
    {{"year": "2000s year", "text": "ONE COMPLETE SENTENCE (20-30 words) describing a major event on {month_name} {day} (2000+). Include context and the significance of the event."}}
  ],
  "PrimeMinister": "Australian PM in {year}",
  "IncomingPM": "The PM who took office AFTER the {year} PM (short). If none/unknown, 'Unknown'.",
  "Monarch": "British monarch in {year}",
  "NRLWinner": "NRL premiers {year} (or 'Unverified - {year} season' if the season had not finished)",
  "AFLWinner": "AFL premiers {year} (or 'Unverified - {year} season')",
  "BestActorName": "Most recent Academy Award Best Actor as of {year}",
  "BestActorFilm": "...their film",
  "BestActressName": "Most recent Academy Award Best Actress as of {year}",
  "BestActressFilm": "...their film",
  "Bathurst": "Bathurst 1000 winner(s) {year}",
  "AusOpenMen": "Australian Open men's singles champion {year}",
  "AusOpenWomen": "Australian Open women's singles champion {year}",
  "SongTitle": "The #1 / top-charting song around {month_name} {year} — ARIA (Australia) if known, else the US Billboard or global #1. ALWAYS give a real, specific song title; NEVER 'Unverified', 'Unknown', 'check ARIA' or any placeholder. If unsure of the exact #1, give the single most popular song of that period.",
  "SongArtist": "The performing artist of that song — always a real name, never a placeholder.",
  "AverageSalary": "Average Australian annual salary {year}, e.g. $95,000",
  "AverageHouse": "Average Australian house price {year}, e.g. $920,000",
  "MilkPrice": "Milk 1L {year}, e.g. $1.60",
  "BreadPrice": "Bread loaf {year}",
  "EggsPrice": "Dozen eggs {year}",
  "PetrolPrice": "Petrol per litre {year}",
  "InflationRate": "Australian inflation {year}, e.g. 5.6%",
  "StampPrice": "Postage stamp {year}",
  "CinemaPrice": "Cinema ticket {year}",
  "CadburyPrice": "Cadbury chocolate bar {year}",
  "WorldPopulation": "World population {year}, e.g. 8.0 billion",
  "AustraliaPopulation": "Australia population {year}, e.g. 26.6 million",
  "TopBook": "Best-selling book of {year} as 'Title - Author'. SUITABLE for a memorial gift — NEVER a book centred on sexual abuse/violence (e.g. NOT 'Lolita'); if the top book is unsuitable, pick another genuinely popular, appropriate one.",
  "TopBookDesc": "One warm, neutral sentence, MAX 18 WORDS.",
  "TVShow": "A popular TV show of {year}",
  "TVShowDesc": "One sentence, MAX 18 WORDS.",
  "FashionTrend": "A defining fashion trend of {year}",
  "FashionDesc": "One sentence, MAX 18 WORDS.",
  "Technology": "A notable technology of {year}",
  "TechDesc": "One sentence, MAX 18 WORDS.",
  "AustraliaBirths": "Approx number of Australian births {year}, e.g. 300,000",
  "BirthsDesc": "One sentence, MAX 18 WORDS."
}}

RULES:
- Remembered: the three people MUST have DIED on {month_name} {day} (verify). Dignified, recognisable.
- If a value is genuinely unknown, write a SHORT placeholder (max 6 words). NEVER write "outside knowledge cutoff" or similar.
- All money in Australian dollars/cents. One sentence per description.
Start with {{ and end with }}."""


def _call_claude(month_name, day, year, api_key, timeout=180):
    headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    body = {"model": CLAUDE_MODEL, "max_tokens": 4096, "temperature": 0.3,
            "messages": [{"role": "user", "content": _prompt(month_name, day, year)}]}
    r = requests.post(CLAUDE_URL, headers=headers, json=body, timeout=timeout)
    if r.status_code != 200:
        raise RuntimeError(f"Claude API error {r.status_code}: {r.text[:300]}")
    text = r.json()["content"][0]["text"].replace("```json", "").replace("```", "").strip()
    a, b = text.find("{"), text.rfind("}")
    if a != -1 and b != -1:
        text = text[a:b + 1]
    return json.loads(text)


# ----------------------------------------------------------------------------
# verified-fact overrides (lookup tables) keyed to the death date/year
# ----------------------------------------------------------------------------
def _apply_overrides(research, day, month, year):
    try:
        lk = LT.resolve_lookup_fields(day, month, year)
    except Exception:
        lk = {}
    pairs = {
        "PrimeMinister": "PrimeMinister", "IncomingPM": "IncomingPM", "Monarch": "Monarch",
        "NRLWinner": "NRLWinner", "AFLWinner": "AFLWinner", "Bathurst": "Bathurst1000",
    }
    for rkey, lkey in pairs.items():
        v = lk.get(lkey)
        if v:
            research[rkey] = v
    # prices / populations with dedicated getters
    getters = {
        "AverageSalary": LT.get_average_salary, "AverageHouse": LT.get_average_house,
        "PetrolPrice": LT.get_petrol_price, "InflationRate": LT.get_inflation_rate,
        "StampPrice": LT.get_stamp_price, "CinemaPrice": LT.get_cinema_price,
        "WorldPopulation": LT.get_world_population, "AustraliaPopulation": LT.get_aus_population,
        "AustraliaBirths": LT.get_australia_births,
    }
    for rkey, fn in getters.items():
        try:
            v = fn(year)
        except Exception:
            v = None
        if v:
            research[rkey] = v
    # Oscars (verified) when present
    try:
        ba = LT.get_oscar_best_actor(year)
        if ba and " - " in ba:
            research["BestActorName"], research["BestActorFilm"] = [x.strip() for x in ba.split(" - ", 1)]
        bs = LT.get_oscar_best_actress(year)
        if bs and " - " in bs:
            research["BestActressName"], research["BestActressFilm"] = [x.strip() for x in bs.split(" - ", 1)]
    except Exception:
        pass
    # Australian Open (single string "Men: X, Women: Y")
    try:
        ao = LT.get_ausopen_winners(year)
        if ao:
            research["_ausopen_full"] = ao
    except Exception:
        pass
    return research


# ----------------------------------------------------------------------------
# public: assemble the render token dict
# ----------------------------------------------------------------------------
def build_pack_data(name, dob, dop, api_key, progress=None):
    """Return (tokens, warnings). dob/dop may be strings (DD/MM/YYYY) or date objects."""
    warnings = []
    if not isinstance(dob, datetime.date):
        dob = parse_date(dob)
    if not isinstance(dop, datetime.date):
        dop = parse_date(dop)
    if dop <= dob:
        raise ValueError("Date of passing must be after the date of birth.")

    year = dop.year
    month_name = MONTHS[dop.month]
    day = dop.day
    weekday = dop.strftime("%A")
    ordd = ordinal(day)

    if progress:
        progress(f"🔍 Researching {month_name} {day}, {year}…")
    research = _call_claude(month_name, day, year, api_key)
    research = _apply_overrides(research, day, dop.month, year)
    # Song: the pack must ALWAYS show a real chart-topper. If the model returned
    # a placeholder ("Unverified", "check ARIA charts May 2026", "Unknown", blank…
    # — which also overflowed the small #1 Single box), fall back to the verified
    # yearly #1 from the lookup table, which always returns a song.
    def _song_placeholder(v):
        s = str(v or "").strip().lower()
        if not s or s in ("unknown", "n/a", "na", "tbc", "none", "-", "—", "tba"):
            return True
        return any(w in s for w in ("unverified", "unavailable", "not available",
                                    "check aria", "aria chart", "to be confirmed",
                                    "to be announced", "cutoff"))
    if _song_placeholder(research.get("SongTitle")) or _song_placeholder(research.get("SongArtist")):
        fb = LT.get_number1_song_fallback(year)
        if fb and " - " in fb:
            research["SongTitle"], research["SongArtist"] = [x.strip() for x in fb.split(" - ", 1)]
        elif fb:
            research["SongTitle"], research["SongArtist"] = fb, ""

    # clean unknown placeholders on short fields
    for k in ("PrimeMinister", "IncomingPM", "Monarch", "NRLWinner", "AFLWinner",
              "Bathurst", "SongTitle", "SongArtist", "AverageSalary", "AverageHouse",
              "MilkPrice", "BreadPrice", "EggsPrice", "PetrolPrice", "InflationRate",
              "StampPrice", "CinemaPrice", "CadburyPrice", "WorldPopulation",
              "AustraliaPopulation", "AustraliaBirths", "TopBook", "TVShow",
              "FashionTrend", "Technology"):
        if k in research:
            research[k] = _clean(research[k])

    ln = life_numbers(dob, dop)
    flower_name, flower_img, fwarn = birth_flower(dob.month)
    if fwarn:
        warnings.append(fwarn)

    # computed years-of-wages (keeps house/salary internally consistent)
    def money(v):
        try:
            n = re.sub(r"[^0-9.]", "", str(v))
            return float(n) if n else None
        except ValueError:
            return None
    hv, sv = money(research.get("AverageHouse")), money(research.get("AverageSalary"))
    if hv and sv and sv > 0:
        yrs = max(1, round(hv / sv))
        years_wages = f"{yrs} year{'s' if yrs != 1 else ''}’ wages"
    else:
        years_wages = _clean(research.get("YearsOfWages", "")) or "—"

    rem = (research.get("Remembered") or [])[:3]
    while len(rem) < 3:
        rem.append({"name": "", "role": ""})
    news = (research.get("News") or [])[:3]
    while len(news) < 3:
        news.append("")
    hist = (research.get("Historical") or [])[:4]
    while len(hist) < 4:
        hist.append({"year": "", "text": ""})

    def work(nm, film):
        nm, film = esc(nm), esc(film)
        return f"{nm} – <i>{film}</i>" if film else nm

    ausopen = research.get("_ausopen_full")
    if not ausopen:
        ausopen = f"Men: {esc(research.get('AusOpenMen',''))}, Women: {esc(research.get('AusOpenWomen',''))}"
    else:
        ausopen = esc(ausopen)

    tokens = {
        # page 1
        "NAME": esc(name).upper(),
        "DATE_LINE": f"{esc(weekday)}, {month_name} {day}<sup>{ordd}</sup> {year}",
        "LIFESPAN": f"{dob.year} – {dop.year}", "AGE": f"{ln['years']} years",
        "PM": esc(research.get("PrimeMinister")), "INCOMING_PM": esc(research.get("IncomingPM")),
        "MONARCH": esc(research.get("Monarch")), "SALARY": esc(commaize(research.get("AverageSalary"))),
        "REM1_NAME": esc(rem[0].get("name")), "REM1_ROLE": esc(rem[0].get("role")),
        "REM2_NAME": esc(rem[1].get("name")), "REM2_ROLE": esc(rem[1].get("role")),
        "REM3_NAME": esc(rem[2].get("name")), "REM3_ROLE": esc(rem[2].get("role")),
        "NEWS1": esc(news[0]), "NEWS2": esc(news[1]), "NEWS3": esc(news[2]),
        "NRL": esc(research.get("NRLWinner")), "AFL": esc(research.get("AFLWinner")),
        "BEST_ACTOR": work(research.get("BestActorName"), research.get("BestActorFilm")),
        "BEST_ACTRESS": work(research.get("BestActressName"), research.get("BestActressFilm")),
        "BATHURST": esc(research.get("Bathurst")), "AUSOPEN": ausopen,
        "WORLD_POP": esc(research.get("WorldPopulation")), "AUS_POP": esc(research.get("AustraliaPopulation")),
        "FLOWER_IMG": flower_img, "FLOWER_NAME": esc(flower_name),
        "SONG": esc(research.get("SongTitle")), "ARTIST": esc(research.get("SongArtist")),
        "AVG_HOUSE": esc(commaize(research.get("AverageHouse"))), "MILK": esc(research.get("MilkPrice")),
        "BREAD": esc(research.get("BreadPrice")), "EGGS": esc(research.get("EggsPrice")),
        # page 2
        "P2_DATE": f"{month_name} {day}<sup>{ordd}</sup>",
        "YEAR1": esc(hist[0].get("year")), "EVENT1": esc(hist[0].get("text")),
        "YEAR2": esc(hist[1].get("year")), "EVENT2": esc(hist[1].get("text")),
        "YEAR3": esc(hist[2].get("year")), "EVENT3": esc(hist[2].get("text")),
        "YEAR4": esc(hist[3].get("year")), "EVENT4": esc(hist[3].get("text")),
        # page 3
        "YEAR": str(year), "YEARS_WAGES": esc(years_wages),
        "PETROL": esc(research.get("PetrolPrice")), "INFLATION": esc(research.get("InflationRate")),
        "STAMP": esc(research.get("StampPrice")), "CINEMA": esc(research.get("CinemaPrice")),
        "CADBURY": esc(research.get("CadburyPrice")),
        # page 4
        "BOOK": esc(research.get("TopBook")), "BOOK_DESC": esc(research.get("TopBookDesc")),
        "TV": esc(research.get("TVShow")), "TV_DESC": esc(research.get("TVShowDesc")),
        "FASHION": esc(research.get("FashionTrend")), "FASHION_DESC": esc(research.get("FashionDesc")),
        "TECH": esc(research.get("Technology")), "TECH_DESC": esc(research.get("TechDesc")),
        "BIRTHS": esc(commaize(research.get("AustraliaBirths"))), "BIRTHS_DESC": esc(research.get("BirthsDesc")),
        # page 5
        "DAYS": ln["days"], "YEARS": str(ln["years"]), "WEEKS": ln["weeks"],
        "MOONS": ln["moons"], "HEARTBEATS": ln["heartbeats"],
    }
    if progress:
        progress("✅ Research complete")
    return tokens, warnings
