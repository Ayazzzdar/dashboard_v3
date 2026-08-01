"""
Lookup Tables Module for Dashboard V3
Loads static, verified reference data (sports winners, awards, PM/Monarch)
from CSV files and resolves them deterministically instead of relying on
the LLM to generate them from training-data recall.

Why this exists:
Fields like NRL winner, AFL winner, Bathurst 1000 winner, Australian Open
winners, Oscar Best Actor/Actress, Prime Minister, and Monarch are finite,
unchanging, already-known historical facts - not generative content. A
hardcoded lookup removes the error category entirely rather than reducing
it through prompt engineering.

Wages, prices, and inflation figures are NOT covered here - those remain
LLM-generated since they vary by month/region/item and don't have one
single canonical correct answer the way a grand final winner does.
"""

import csv
import os
from datetime import date, datetime
from pathlib import Path
from typing import Optional, Dict

# Directory containing all the lookup CSV files. Defaults to a 'data'
# folder sitting next to this file - keeps things portable regardless
# of where the dashboard is deployed from.
DATA_DIR = Path(__file__).parent / "data"


def _load_year_table(filename: str) -> Dict[int, dict]:
    """Load a simple year -> row CSV into a dict keyed by integer year.
    Used for NRL, AFL, Bathurst, Oscars, Australian Open tables.
    """
    table = {}
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return table
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                year = int(row['year'])
            except (KeyError, ValueError):
                continue
            table[year] = row
    return table


def _load_date_range_table(filename: str) -> list:
    """Load a date-range CSV (start_date, end_date, name, ...) into a
    sorted list of dicts. Used for PM and Monarch tables, since these
    change mid-year rather than aligning to calendar years.
    """
    rows = []
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return rows
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                row['_start'] = datetime.strptime(row['start_date'], '%Y-%m-%d').date()
                row['_end'] = datetime.strptime(row['end_date'], '%Y-%m-%d').date()
            except (KeyError, ValueError):
                continue
            rows.append(row)
    rows.sort(key=lambda r: r['_start'])
    return rows


def _load_dayofyear_table(filename: str) -> Dict[tuple, dict]:
    """Load a day-of-year CSV keyed by an integer (month, day) tuple.
    Used for facts tied to a calendar date regardless of year - e.g.
    famous people born on a given day. First two columns MUST be
    'month' and 'day' (1-12 and 1-31).
    """
    table = {}
    filepath = DATA_DIR / filename
    if not filepath.exists():
        return table
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                key = (int(row['month']), int(row['day']))
            except (KeyError, ValueError):
                continue
            table[key] = row
    return table


# Load all tables once at import time. Streamlit re-imports modules
# fairly rarely during a session, so this is cheap and avoids re-reading
# CSVs on every single order processed.
_NRL_TABLE = _load_year_table("nrl_winners.csv")
_AFL_TABLE = _load_year_table("afl_winners.csv")
_BATHURST_TABLE = _load_year_table("bathurst_winners.csv")
_AUSOPEN_TABLE = _load_year_table("ausopen_winners.csv")
_OSCAR_TABLE = _load_year_table("oscar_winners.csv")
_SALARY_TABLE = _load_year_table("average_salary.csv")
_SONG_TABLE = _load_year_table("number1_songs.csv")
_PETROL_TABLE = _load_year_table("petrol_prices.csv")
_INFLATION_TABLE = _load_year_table("inflation_rates.csv")
_AUS_POP_TABLE = _load_year_table("aus_population.csv")
_WORLD_POP_TABLE = _load_year_table("world_population.csv")
_STAMP_TABLE = _load_year_table("stamp_prices.csv")
_BABY_NAMES_TABLE = _load_year_table("baby_names.csv")
_BIRTHS_TABLE = _load_year_table("aus_births.csv")
_HOUSE_TABLE = _load_year_table("average_house.csv")
_CELEBRITY_TABLE = _load_dayofyear_table("celebrity_birthdays.csv")
_PM_TABLE = _load_date_range_table("pm_terms.csv")
_MONARCH_TABLE = _load_date_range_table("monarchs.csv")


def get_nrl_winner(year: int) -> Optional[str]:
    """Return the verified NRL/NSWRL premiership winner for a given year,
    or None if the year isn't in the table (falls back to LLM generation)."""
    row = _NRL_TABLE.get(year)
    if not row:
        return None
    return row.get('winner', '').strip() or None


def get_afl_winner(year: int) -> Optional[str]:
    """Return the verified AFL/VFL premiership winner for a given year,
    or None if the year isn't in the table (falls back to LLM generation)."""
    row = _AFL_TABLE.get(year)
    if not row:
        return None
    return row.get('winner', '').strip() or None


def get_bathurst_winner(year: int) -> Optional[str]:
    """Return the verified Bathurst 1000 winning driver(s) for a given
    year, or None if the year isn't in the table. Years before 1960
    intentionally have no entry, since the race did not yet exist -
    this returns None so the LLM is not consulted, and the dashboard
    should display a 'Not held' message for those years instead of
    silently falling through to the LLM (see resolve_bathurst below)."""
    row = _BATHURST_TABLE.get(year)
    if not row:
        return None
    return row.get('winner', '').strip() or None


def resolve_bathurst(year: int) -> str:
    """Bathurst-specific resolver that distinguishes between 'not in our
    table yet' (fall back to LLM) and 'genuinely not held that year'
    (explicit message, no LLM fallback). The race began in 1960."""
    winner = get_bathurst_winner(year)
    if winner:
        return winner
    if year < 1960:
        return f"Not held - the Bathurst 1000 began in 1960"
    return None  # Outside table range for some other reason - let LLM attempt


def get_ausopen_winners(year: int) -> Optional[str]:
    """Return the verified Australian Open singles champions (men and
    women) for a given year, formatted as 'Men: X, Women: Y', or None
    if the year isn't in the table. Explicitly flags years the
    tournament was not held (1941-1945 WWII, 1986 calendar shift)."""
    row = _AUSOPEN_TABLE.get(year)
    if not row:
        return None
    mens = row.get('mens_winner', '').strip()
    womens = row.get('womens_winner', '').strip()
    if mens == 'Not held' or womens == 'Not held':
        notes = row.get('notes', '').strip()
        return notes if notes else "Not held this year"
    if not mens or not womens:
        return None
    return f"Men: {mens}, Women: {womens}"


def get_oscar_best_actor(year: int) -> Optional[str]:
    """Return the verified Oscar Best Actor winner and film for a given
    year, formatted as 'Name - Film', or None if not in the table."""
    row = _OSCAR_TABLE.get(year)
    if not row:
        return None
    actor = row.get('best_actor', '').strip()
    film = row.get('best_actor_film', '').strip()
    if not actor:
        return None
    return f"{actor} - {film}" if film else actor


def get_oscar_best_actress(year: int) -> Optional[str]:
    """Return the verified Oscar Best Actress winner and film for a given
    year, formatted as 'Name - Film', or None if not in the table."""
    row = _OSCAR_TABLE.get(year)
    if not row:
        return None
    actress = row.get('best_actress', '').strip()
    film = row.get('best_actress_film', '').strip()
    if not actress:
        return None
    return f"{actress} - {film}" if film else actress


def _find_in_date_range(table: list, target: date) -> Optional[dict]:
    """Find the row in a date-range table whose start/end span contains
    the target date. Returns the row dict, or None if outside all ranges
    (e.g. a birthdate before the table's earliest covered date)."""
    for row in table:
        if row['_start'] <= target <= row['_end']:
            return row
    return None


def get_pm_and_incoming(day: int, month: int, year: int) -> tuple:
    """Return (PrimeMinister, IncomingPM) for a given birthdate.

    IncomingPM is derived automatically from the table's ordering rather
    than being a separate lookup - it is simply 'whoever comes next in
    the sequence after the PM in office on this date'. This guarantees
    PM and IncomingPM can never contradict each other, which was
    previously possible when both were independently LLM-generated.

    Returns (None, None) if the birthdate falls outside the table's
    covered range (before 1929), so the caller can fall back to the LLM.
    """
    try:
        target = date(year, month, day)
    except ValueError:
        return (None, None)

    current_idx = None
    for i, row in enumerate(_PM_TABLE):
        if row['_start'] <= target <= row['_end']:
            current_idx = i
            break

    if current_idx is None:
        return (None, None)

    current_pm = _PM_TABLE[current_idx].get('name', '').strip()

    # IncomingPM = next distinct name in the sequence after this one
    incoming_pm = None
    for j in range(current_idx + 1, len(_PM_TABLE)):
        candidate = _PM_TABLE[j].get('name', '').strip()
        if candidate and candidate != current_pm:
            incoming_pm = candidate
            break

    return (current_pm or None, incoming_pm)


def get_monarch(day: int, month: int, year: int) -> Optional[str]:
    """Return the reigning British monarch for a given birthdate, or
    None if the birthdate falls outside the table's covered range
    (before 1910), so the caller can fall back to the LLM."""
    try:
        target = date(year, month, day)
    except ValueError:
        return None
    row = _find_in_date_range(_MONARCH_TABLE, target)
    if not row:
        return None
    return row.get('name', '').strip() or None


def get_number1_song_fallback(year: int) -> Optional[str]:
    """Return the yearly #1 song as a FALLBACK only — used when the LLM
    returns 'unknown', blank, or an invalid response for Number1Song.
    Also used as the definitive answer for 2026 (current year, no full
    year data yet) and any future year.
    
    NOT used to override the LLM for historical years — the LLM tries
    first to find a song close to the birth date. This table only kicks
    in when the LLM fails or the year is 2026+.
    """
    row = _SONG_TABLE.get(year)
    if not row:
        # For any year beyond our table, return the latest known #1
        latest_year = max(_SONG_TABLE.keys()) if _SONG_TABLE else None
        if latest_year:
            row = _SONG_TABLE.get(latest_year)
    if not row:
        return None
    return row.get('number1_song', '').strip() or None


def get_average_salary(year: int) -> Optional[str]:
    """Return the verified average annual salary for a given year in AUD,
    or None if the year isn't in the table (falls back to LLM generation).
    1920-1975: sourced from DailyCare/historical wage records (interpolated).
    1976-2025: sourced from ABS Average Weekly Earnings (Cat 6350.0/6302.0) x52.
    """
    row = _SALARY_TABLE.get(year)
    if not row:
        return None
    return row.get('average_annual_salary', '').strip() or None


def get_petrol_price(year: int) -> Optional[str]:
    """Return the verified average petrol price for a given year in AUD.
    1926-2016: official BITRE Information Sheet 82 series.
    2017-2025: AIP/ACCC annual retail averages.
    1920-1925: estimated (pre-BITRE series).
    Returns None if year not in table (falls back to LLM generation)."""
    row = _PETROL_TABLE.get(year)
    if not row:
        return None
    return row.get('petrol_price', '').strip() or None


def get_inflation_rate(year: int) -> Optional[str]:
    """Return the verified annual inflation rate for a given year.
    1949-2025: official ABS CPI annual figures.
    1920-1948: RBA pre-CPI retail price index series (approximate).
    Returns None if year not in table (falls back to LLM generation)."""
    row = _INFLATION_TABLE.get(year)
    if not row:
        return None
    return row.get('inflation_rate', '').strip() or None


def get_aus_population(year: int) -> Optional[str]:
    """Return verified Australian population for a year, or None if the
    year isn't in the table (falls back to LLM generation).
    Source: ABS historical population + Census + ERP; UN midyear estimates."""
    row = _AUS_POP_TABLE.get(year)
    if not row:
        return None
    return row.get('aus_population', '').strip() or None


def get_world_population(year: int) -> Optional[str]:
    """Return verified world population for a year, or None if the year
    isn't in the table (falls back to LLM generation).
    Source: UN World Population Prospects + US Census Bureau historical."""
    row = _WORLD_POP_TABLE.get(year)
    if not row:
        return None
    return row.get('world_population', '').strip() or None


def get_stamp_price(year: int) -> Optional[str]:
    """Return the verified basic domestic letter postage rate in effect
    during a year, or None if not in table (falls back to LLM generation).
    Source: Australia Post basic postage rate history (Wikipedia/Stampboards)."""
    row = _STAMP_TABLE.get(year)
    if not row:
        return None
    return row.get('stamp_price', '').strip() or None


def get_boy_name(year: int, rank: int) -> Optional[str]:
    """Return the verified NSW-registry top-10 boys' name at a given rank
    (1-10) for a year, or None if the year isn't in the table or the cell
    is blank (falls back to LLM generation).
    Source: NSW Registry of Births, Deaths & Marriages, official
    'Popular Baby Names 1952-2025' dataset (Data.NSW). Covers 1952-2025;
    2026 carries forward the most-recent (2025) list. Pre-1952 has no
    official registry data, so those years return None by design."""
    if rank < 1 or rank > 10:
        return None
    row = _BABY_NAMES_TABLE.get(year)
    if not row:
        return None
    return row.get(f'boy{rank}', '').strip() or None


def get_girl_name(year: int, rank: int) -> Optional[str]:
    """Return the verified NSW-registry top-10 girls' name at a given rank
    (1-10) for a year, or None if the year isn't in the table or the cell
    is blank (falls back to LLM generation).
    Source: NSW Registry of Births, Deaths & Marriages, official
    'Popular Baby Names 1952-2025' dataset (Data.NSW). Covers 1952-2025;
    2026 carries forward the most-recent (2025) list. Pre-1952 has no
    official registry data, so those years return None by design."""
    if rank < 1 or rank > 10:
        return None
    row = _BABY_NAMES_TABLE.get(year)
    if not row:
        return None
    return row.get(f'girl{rank}', '').strip() or None


def get_australia_births(year: int) -> Optional[str]:
    """Return the verified/estimated Australian total births for a year, or
    None if the year isn't in the table (falls back to LLM generation).
    Source: ABS Births, Australia (cat. 3301.0) registered births; pre-1924
    and 2025+ rows are estimates/carry-forward as flagged in the CSV."""
    row = _BIRTHS_TABLE.get(year)
    if not row:
        return None
    return row.get('aus_births', '').strip() or None


def get_average_house(year: int) -> Optional[str]:
    """Return the average Australian house price for a year in AUD, or None
    if the year isn't in the table (falls back to LLM generation).
    Source: ABS RPPI / Abelson & Chung national estimates (post-1970 solid);
    pre-1970 rows are flagged estimates in the CSV, per limited national data."""
    row = _HOUSE_TABLE.get(year)
    if not row:
        return None
    return row.get('average_house', '').strip() or None


def get_celebrity(month: int, day: int, rank: int) -> Optional[str]:
    """Return a verified famous person born on this calendar day (month+day)
    at slot 1-3, formatted 'Name - Profession', or None if the day isn't in
    the table or the cell is blank (falls back to LLM generation).

    Birthdays are date-of-year facts (not year facts), so this is keyed by
    (month, day) and ignores the birth year. Every entry is an individually
    verified birthday - the whole point of this table is to remove the
    wrong-birth-date errors the LLM produces (e.g. placing a celebrity on
    the wrong day). A missing day returns None and the LLM value stands."""
    if rank < 1 or rank > 3:
        return None
    row = _CELEBRITY_TABLE.get((month, day))
    if not row:
        return None
    return row.get(f'celebrity{rank}', '').strip() or None


def resolve_lookup_fields(day: int, month: int, year: int) -> Dict[str, Optional[str]]:
    """Master resolver - call this once per order to get every lookup-
    table-backed field in one go. Returns a dict where any field that
    could not be resolved from the tables is set to None; the caller
    should leave the corresponding LLM-generated value untouched in
    that case (i.e. only override fields that resolved successfully).
    """
    pm, incoming_pm = get_pm_and_incoming(day, month, year)
    return {
        "Celebrity1": get_celebrity(month, day, 1),
        "Celebrity2": get_celebrity(month, day, 2),
        "Celebrity3": get_celebrity(month, day, 3),
        "NRLWinner": get_nrl_winner(year),
        "AFLWinner": get_afl_winner(year),
        "Bathurst1000": resolve_bathurst(year),
        "AusOpenWinners": get_ausopen_winners(year),
        "BestActor": get_oscar_best_actor(year),
        "BestActress": get_oscar_best_actress(year),
        "PrimeMinister": pm,
        "IncomingPM": incoming_pm,
        "Monarch": get_monarch(day, month, year),
        "AverageSalary": get_average_salary(year),
        "PetrolPrice": get_petrol_price(year),
        "InflationRate": get_inflation_rate(year),
        "AustraliaPopulation": get_aus_population(year),
        "WorldPopulation": get_world_population(year),
        "StampPrice": get_stamp_price(year),
        "BoyName1": get_boy_name(year, 1),
        "BoyName2": get_boy_name(year, 2),
        "BoyName3": get_boy_name(year, 3),
        "BoyName4": get_boy_name(year, 4),
        "BoyName5": get_boy_name(year, 5),
        "BoyName6": get_boy_name(year, 6),
        "BoyName7": get_boy_name(year, 7),
        "BoyName8": get_boy_name(year, 8),
        "BoyName9": get_boy_name(year, 9),
        "BoyName10": get_boy_name(year, 10),
        "GirlName1": get_girl_name(year, 1),
        "GirlName2": get_girl_name(year, 2),
        "GirlName3": get_girl_name(year, 3),
        "GirlName4": get_girl_name(year, 4),
        "GirlName5": get_girl_name(year, 5),
        "GirlName6": get_girl_name(year, 6),
        "GirlName7": get_girl_name(year, 7),
        "GirlName8": get_girl_name(year, 8),
        "GirlName9": get_girl_name(year, 9),
        "GirlName10": get_girl_name(year, 10),
        "AustraliaBirths": get_australia_births(year),
        "AverageHouse": get_average_house(year),
    }
