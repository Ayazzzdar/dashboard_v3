# The Day Archive — CRO work handover

**Session date:** 14–21 October 2026
**Store:** The Day Archive (thedayarchive.com, AUD, Shopify plan)
**Repo branch:** `claude/nifty-wright-xza7lh`

This is everything needed to pick the work up on a local machine. It covers what
exists, what was decided and why, what is broken, and what to do next.

---

## 1. Current state at a glance

### Shopify themes

| Theme | ID | Role | What it is |
|---|---|---|---|
| `theme day archive` | `154012647579` | **MAIN (live)** | Untouched all session. Nothing was published. |
| `Copy of theme day archive` | `154637729947` | unpublished | Stale, from April 2026. Ignore. |
| `CRO v4 — Page-2 Format + Trust Stack` | `159801344155` | unpublished | Structure work. Fallback. |
| `CRO v5 — Redesign (2026-10-19)` | `160000934043` | unpublished | **The current build.** Duplicated from v4. |

**The live theme was never modified.** Every change is in v4/v5, both unpublished.

### Products

| Handle | Status | Price | Compare-at | Template suffix |
|---|---|---|---|---|
| `the-birth-day-archive-pack` | ACTIVE | **$59.99** | $100.00 | *(none)* → `product.json` |
| `page-2` | UNLISTED | **$69.99** | $115.00 | `page-2` → `product.page-2.json` |
| `frame-your-order` | ACTIVE | $40.00 | — | |
| `frame-your-order™` | UNLISTED | $30.00 | $40.00 | variant `48940258918555` |
| `gift-card` | ACTIVE | $20–$500 | — | $20 variant `49514465558683` |

**Important:** in v5 the redesign is on `templates/product.json`, so it shows on
**`the-birth-day-archive-pack`**. `templates/product.page-2.json` is still the
original 62,594-byte page-2 and is untouched — previewing `/products/page-2`
will show the OLD look.

Preview URL:
```
https://thedayarchive.com/products/the-birth-day-archive-pack?preview_theme_id=160000934043
```

---

## 2. The evidence base

Two post-purchase survey exports, cross-checked against the Grapevine connector
(which reported the same 537 responses for the last 180 days).

- Grapevine export (180 days): **537** responses
- Post-purchase export (May 2026): **449** responses
- **Combined: 986**

### Why people buy (n=805 who answered)

| Share | Customer's own wording |
|---|---|
| 51.8% | "It felt more unique than typical gifts" |
| 40.4% | "I thought they'd love the nostalgia factor" |
| 19.6% | "It felt genuinely meaningful, not just personalised" |
| 6.8% | "I was stuck on what to get them" |
| 6.6% | "The quality and presentation looked premium" |

### What almost stopped them (n=579)

| Share | Objection |
|---|---|
| 39.0% | Nothing — bought straight away |
| 17.8% | The price felt a little high |
| 16.4% | Wasn't sure if the quality would match |
| 15.9% | Wasn't sure how accurate the content would be |
| 14.3% | Worried about delivery time |
| 6.7% | The shipping cost |

### Audience

- **91.6% buy it as a gift**, 8.4% for themselves.
- Milestone-heavy: 60th, 70th, 80th, 50th, 90th+, 40th. Recipients skew old.
- Recipients: friend, sibling, husband/wife, parent, son/daughter, partner.

### Unprompted free-text blockers (not in any multiple choice)

These came up repeatedly and were not addressed anywhere on the page:

- "Making sure it was Australian based. NO content from USA"
- "CHECKED IF WAS IN AUS DOLLARS"
- "Wasn't sure if it was coming from Australia. Contact form didn't give me any
  location details. Google searched my answer."
- "Worried you are a scam" / "Not sure if I an going to be scammed"
- "There was no PayPal for payment. Wasn't keen to put my Credit card number in"
- "Bpay wasnt an option for payment"
- "the repeated offers at the end about adding a frame almost made me stop the order"

### Grapevine survey performance

537 responses, 1,294 unique impressions, 28.9% response rate,
**63.7% completion**, $45,744 attributed revenue.

| Channel | Responses | Completion |
|---|---|---|
| Thank You Page | 391 | 68.8% |
| Order Status Page (Checkout Extension) | 146 | 50.0% |

195 people start and never finish. Drop-off by question:

| Question | Answered | Drop |
|---|---|---|
| Who is this for? | 537 | — |
| Which birthday? | 476 | −61 |
| What made you decide to buy? | 455 | −21 |
| **What were you looking at before you found us?** (open text) | **387** | **−68** |
| Anything almost stopped you? | 374 | −13 |
| Other keepsake products? | 362 | −12 |
| Upgrades you'd pay extra for? | 342 | −20 |

**Fix:** the open-text question is the worst drop and returns mostly "Nothing"
and "Facebook". Convert to multiple choice or move it last, and move the two
commercially valuable questions (upgrades, other products) earlier — they
currently sit where drop-off is worst, which is why they have the smallest
samples.

---

## 3. The 10-page decision (recommendation: don't)

When asked what they'd pay extra for, **not one customer asked for more pages**.
95 of 342 said they would not pay extra for anything. What they would pay for:

| Demand | Upgrade |
|---|---|
| ~75 | A premium leather-look folder |
| ~70 | Gold foil lettering on the folder |
| ~55 | **A personal message page** |
| ~35 | A linen-wrapped presentation box |
| — | Choice of paper / folder colour |

A **personal message page** is the standout: effectively a paid 6th page, zero
factual risk, and it strengthens the gift framing 91.6% of buyers are there for.
Doubling to 10 researched pages doubles the factual-error surface on a product
sold with a lifetime replacement guarantee.

Highest-demand new products: Newspaper Broadsheet Print (43), Surname Archive
Pack (42), Wedding Anniversary Archive Pack (25), Leather-Bound Book (22).

---

## 4. What is in CRO v5

### The architecture decision that matters

`templates/product.json` already renders my snippets via `{% render %}`. So the
entire redesign ships as **a CSS asset plus snippet rewrites, without touching
the product template at all**. That means the cart JavaScript
(`tda-pack-multi`, `tda-frame-upsell`) was never re-transmitted and cannot have
been corrupted.

**To revert the whole redesign:** delete the `{{ 'tda-redesign.css' | asset_url
| stylesheet_tag }}` line from `snippets/tda-bullets.liquid`.

### Files in v5 (all verified byte-perfect by md5 on upload)

| File | Bytes | md5 |
|---|---|---|
| `assets/tda-redesign.css` | 8862 | `30ebf4fade42f1dd4ffc16c74bdeddd1` |
| `assets/tda-preview.json` | 18408 | `41aa74f997a92179d9bfd343e409e071` |
| `snippets/tda-bullets.liquid` | 9932 | `19a7bbf59ec3e9007734a059fe11f819` |
| `snippets/tda-trust-bar.liquid` | 2484 | `4c0bb22aa373341140e54919219caa66` |
| `snippets/tda-pack-multi.liquid` | 18208 | inherited from v4, untouched |
| `snippets/tda-frame-upsell.liquid` | 16247 | inherited from v4, untouched |
| `templates/product.json` | 31484 | inherited from v4, untouched in v5 |

Pull them locally with the Shopify CLI:

```bash
shopify theme pull --store thedayarchive.myshopify.com --theme 160000934043
```

### The design system (`assets/tda-redesign.css`)

Font and palette are **unchanged** from the live theme. All improvements are
hierarchy, scale, radius and spacing.

```css
--tda-text: 1.3rem;      /* benefits, preview input/button, facts */
--tda-text-sm: 1.2rem;   /* sub-text, notes, trust items */
```

Change those two values to resize every custom block at once.

- Radii **18–40px → 4px** (via Dawn's own custom properties)
- Headings to **weight 700** (same Harmonia Sans — 700 maps to the bolder face
  Dawn already loads; the live theme uses `harmonia_sans_n4` for *both*
  headings and body, so nothing led the eye)
- Removed the `.product__info-container` font-size override so the product
  column keeps the theme's own sizing and custom blocks never out-scale the
  real personalisation fields

**Contrast rule:** amber `#EF9F27` is a **fill behind navy text only**, never
text on white — it only reaches 2.2:1. Navy on amber is 5.0:1. Secondary text
uses mid-navy `#556E8C` (5.2:1 on white).

### Palette (unchanged, from `config/settings_data.json`)

```
navy      #1E3A5F   ink, buttons, headings
white     #FFFFFF
pale blue #EFF0F5   panels
rule grey #E3E4E9   hairlines
cream     #F5F0E8   warm bands
amber     #EF9F27   accent FILL only
red       #C72329   errors only
mid navy  #556E8C   secondary text (derived, not in original palette)
```

### Copy changes already made (in v4's `templates/product.json`)

- Benefit bullets lead with the #1 survey driver, verbatim
- FAQ tabs reordered by **measured objection frequency**, with a new
  **"Is it worth the price?"** tab for the #1 objection (17.8%) that the page
  had no answer for
- Replaced `"Only 7 printing slots left this week"` with
  `"Order today — dispatched within 48 hours, Mon–Fri"`. Invented scarcity is
  the wrong play for an audience already asking "is this a scam", and
  unsubstantiated scarcity carries Australian Consumer Law risk.
- Buy-box trust block answering the Australian / legitimacy doubt

---

## 5. The "see your date before you buy" preview

Borrowed from The Night Sky. Targets the accuracy (15.9%) and quality (16.4%)
objections by showing real records instead of promising them.

### How it works — no API, no server, no LLM

`lookup_tables.resolve_lookup_fields(day, month, year)` already existed and
returns every deterministic field for a date. Every CSV in `data/` is keyed by
`year`, except `celebrity_birthdays.csv` (`month,day`) and PM/monarch (date
ranges). It is a pure table lookup.

`build_preview_json.py` (committed) reads the CSVs and emits
`assets/tda-preview.json` — **130 years (1897–2026), 18KB**, uploaded as a theme
asset and fetched client-side.

```bash
python3 build_preview_json.py                 # writes tda-preview.json
python3 build_preview_json.py out/preview.json
```

Then upload the result to the theme as `assets/tda-preview.json`.

### Two rules that must hold

1. **Only deterministic CSV-backed fields.** Never the generated page copy. If
   the preview contradicted the printed pack, a customer could screenshot it.
2. **Don't render page 1.** Show a few facts plus "the full 5 pages unlock with
   your order". Showing the whole page delivers the value before payment.

### Currently displays 5 facts

Prime Minister · Number one song · Average house · Average salary · NRL premiers

AFL and monarch were removed from the **display only** — they are still in the
JSON asset, so adding either back is one `addFact(...)` line, no rebuild.

### Date input

Auto-inserts slashes as you type (`12031995` → `12/03/1995`), matching the
`DD/MM/YYYY` behaviour of the pack-multi birthday fields. Backspace walks all
the way back without sticking; paste normalises `-` and `.` separators; input is
capped at 8 digits; Enter is intercepted so it cannot submit the product form.

### Free trust win not yet used

Every CSV has a **`source` column**. Showing "Source: ABS" beside a figure
directly answers the 15.9% accuracy objection, and neither competitor does it.

---

## 6. Known problems — read before publishing

### A. The page is too busy (unresolved, and the main open question)

**Root cause:** the approved mockup had a **3-step configurator**
(*1. The date → 2. Personalise → 3. Gift options*) which hid two-thirds of the
decisions until needed. What shipped is a **CSS restyle that kept the original
block order** — chosen deliberately to avoid re-transmitting cart code. The page
has the new skin but not the new structure: ~20 rendering blocks in the old order.

**Worst symptom — two date fields.** The buy box asks for the birthday twice:
once in the preview module, once in the real `Birthday` personalisation field.
A customer who uses the preview does the same work twice.

**Redundancy.** "Dispatched in 48 hours / tracked delivery" appears in **four**
places: the trust bar, the shipping checkpoints timeline, the alert line, and
the delivery FAQ tab. The guarantee appears three times.

**Three options:**

1. **Trim only** (low risk, snippet-level): drive the preview off the real
   Birthday field instead of its own input; cut the alert line and one delivery
   mention. Removes a duplicate form field and two redundant blocks.
2. **Build the actual stepper** (real risk): collapse personalisation + 2nd
   archive + frame into the three numbered steps. Needs the product template
   rewritten and the pack-multi / frame-upsell JS rehomed.
3. **Leave it and A/B test.** "Feels busy" is a hypothesis, not a measurement.

Recommendation: do 1, then let a test decide 2.

### B. Data quality issues the preview now exposes

1. **Pre-1960s songs are US chart entries.** 1946 returns "Prisoner of Love –
   Perry Como"; the CSV's own source column says *"US (pre-chart era)"*. The
   page claims "Made for Australians. By Australians." and has an
   "Is it really Australian?" FAQ — an 80th or 90th birthday buyer sees an
   American song. Those are two of the biggest milestone segments.
2. **2026 duplicates 2025's song** ("Die with a Smile") — placeholder data.
3. **2026 salary is `$88,000`** while every other year is unformatted
   (`$84812`). Now one of only 5 displayed facts, so it is visible.

### C. Lookup table coverage gaps

| Table | Starts |
|---|---|
| `afl_winners.csv` | 1897 |
| `nrl_winners.csv` | 1908 |
| most others | 1920 |
| `ausopen_winners.csv`, `oscar_winners.csv` | 1930 |
| **`baby_names.csv`** | **1952** |
| `bathurst_winners.csv` | 1960 |
| `cinema_prices.csv` | 1976 |

Someone turning 80 was born ~1946 and 90 ~1936 — **both before `baby_names`
starts**, and page 5 of the pack *is* "Top 20 Baby Names of Your Birth Year".
Roughly a fifth of milestone buyers get a 5-page pack whose page 5 has no source
data. **Check what `page5_names.py` does for a pre-1952 year.**

### D. Payment friction (possible lost revenue)

From survey verbatims: no PayPal, no BPAY, "Wasn't keen to put my Credit card
number in". Worth checking what is actually enabled at checkout.

### E. Never render-tested

Everything was verified at **file level** (md5 on every upload), not visually.
This environment could not reach the storefront. Before publishing, preview and
check:

- Add to cart for 1 pack, and for 2+ packs (the free $20 gift card path)
- The frame upsell and its quantity picker
- The preview with a valid date, an invalid date, and a pre-1920 date
- The date field: type, backspace through it, paste one in

---

## 7. Pricing test — not started, deliberately

`page-2` is live at **$69.99 / $115**; the original is **$59.99 / $100**. Price
is a product-level field, so changing it hits the live store immediately. It was
left alone.

**Run format first at the current price, then price separately.** Changing both
at once makes the result unreadable — which is exactly the confound that already
exists between the two pages.

---

## 8. Getting a second URL for testing

| Option | URL | Trade-off |
|---|---|---|
| **Theme preview** | `?preview_theme_id=160000934043` | Zero risk, available now. Cookie-based — not for paid traffic. |
| **Alternate template** | `?view=v5` | Real URL, one product, reviews/analytics stay unified. Needs new files added to the **live** theme (additive only — `product.json` untouched). |
| **Duplicate product** | new handle | Clean separate URL, but splits Judge.me reviews (new product starts at zero, which undermines the trust stack being tested) and analytics. |
| **A/B app** (Shoplift, Intelligems) | — | The only option that gives a trustworthy conversion number. |

If measuring CR: use the A/B app pointed at live theme vs v5. Don't use a
duplicate product — zero reviews would bias the test against the redesign.

---

## 9. Competitor notes

- **A Day in History** — closest competitor, originally copied. Their update was
  ~20% "more pages", 80% offer + trust + gift positioning: page-count badge,
  "Handmade in the USA", 1,857 reviews with photo/video, lifetime replacement
  guarantee, scarcity, free gift folder, benefit-named sections.
  Their "US-based team" is their moat for US buyers — **Australian-made is the
  counter-position**, and the survey confirms customers care.
- **Historic Newspapers** — `MAKE YOUR BOOK` numbered configurator
  (1. Design the cover → 2. Add Personalisation → 3. Select gift options),
  uppercase bold H1, price + "Tax included.", vertical thumbnail rail,
  verified-customer review rows, dark FAQ band.
- **The Night Sky** — the live preview *is* the hero; step rail
  (1. Format → 2. Personalize → 3. Finish); segmented option tiles.

Both competitors converge on the same pattern: **the buy box is a task to
complete, not copy to read.** Neither sells from bullets.

---

## 10. Repo files added this session

| File | What |
|---|---|
| `CRO_NOTES.md` | v4 build notes + full survey evidence |
| `build_preview_json.py` | Builds `assets/tda-preview.json` from `data/*.csv` |
| `HANDOVER_CRO.md` | This file |

Commits on `claude/nifty-wright-xza7lh`:

```
Add CRO v4 build notes from post-purchase survey analysis
Add storefront preview dataset generator
```

---

## 11. Suggested order of work

1. **Trim the busyness** — drive the preview off the real Birthday field, cut
   the duplicate delivery mentions. Snippet-level, low risk.
2. **Fix the three data issues** (2026 song, 2026 salary format, pre-1960s US
   songs) — these are now customer-visible.
3. **Check `page5_names.py`** for pre-1952 years.
4. **Preview and click-test** the cart paths listed in §6E.
5. **Set up the A/B test** properly before drawing conclusions.
6. Then decide on the full 3-step stepper.
7. Separately: fix the Grapevine survey question order, and add a **personal
   message page** to the product rather than expanding to 10 pages.
