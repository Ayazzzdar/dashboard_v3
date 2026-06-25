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


# Load all tables once at import time. Streamlit re-imports modules
# fairly rarely during a session, so this is cheap and avoids re-reading
# CSVs on every single order processed.
_NRL_TABLE = _load_year_table("nrl_winners.csv")
_AFL_TABLE = _load_year_table("afl_winners.csv")
_BATHURST_TABLE = _load_year_table("bathurst_winners.csv")
_AUSOPEN_TABLE = _load_year_table("ausopen_winners.csv")
_OSCAR_TABLE = _load_year_table("oscar_winners.csv")
_SALARY_TABLE = _load_year_table("average_salary.csv")
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


def resolve_lookup_fields(day: int, month: int, year: int) -> Dict[str, Optional[str]]:
    """Master resolver - call this once per order to get every lookup-
    table-backed field in one go. Returns a dict where any field that
    could not be resolved from the tables is set to None; the caller
    should leave the corresponding LLM-generated value untouched in
    that case (i.e. only override fields that resolved successfully).
    """
    pm, incoming_pm = get_pm_and_incoming(day, month, year)
    return {
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
    }
