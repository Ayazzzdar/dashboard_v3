# The Day Archive — CRO v4 build notes

Theme: **CRO v4 — Page-2 Format + Trust Stack (2026-10-14)**
`gid://shopify/OnlineStoreTheme/159801344155` — **UNPUBLISHED**
Duplicated from the live theme `theme day archive` (154012647579). The live
theme was not modified.

## Evidence base

Two post-purchase survey exports, cross-checked against the Grapevine
connector (which reports the same 537 responses for the last 180 days).

| Source | Responses |
|---|---|
| Grapevine export (180 days) | 537 |
| Post-purchase export (May 2026) | 449 |
| **Combined** | **986** |

### Why people buy (n=805 who answered)
| Share | Customer's own wording |
|---|---|
| 51.8% | "It felt more unique than typical gifts" |
| 40.4% | "I thought they'd love the nostalgia factor" |
| 19.6% | "It felt genuinely meaningful, not just personalised" |
| 6.8% | "I was stuck on what to get them" |
| 6.6% | "The quality and presentation looked premium" |

### What almost stopped them (n=579 who answered)
| Share | Objection |
|---|---|
| 39.0% | Nothing — bought straight away |
| 17.8% | The price felt a little high |
| 16.4% | Wasn't sure if the quality would match |
| 15.9% | Wasn't sure how accurate the content would be |
| 14.3% | Worried about delivery time |
| 6.7% | The shipping cost |

### Audience
- **91.6% buy it as a gift**, only 8.4% for themselves.
- Milestone-heavy: 60th, 70th, 80th, 50th, 90th+, 40th. Recipients skew older.
- Recipients: friend, sibling, husband/wife, parent, son/daughter, partner.

### Unprompted free-text blockers (not in any multiple choice)
These came up repeatedly and were **not** addressed anywhere on the page:
- "Making sure it was Australian based. NO content from USA"
- "CHECKED IF WAS IN AUS DOLLARS"
- "Wasn't sure if it was coming from Australia. Contact form didn't give me
  any location details. Google searched my answer."
- "Worried you are a scam" / "Not sure if I an going to be scammed"
- "There was no PayPal for payment. Wasn't keen to put my Credit card number in"
- "Bpay wasnt an option for payment"
- "the repeated offers at the end about adding a frame almost made me stop the order"

## What changed in this theme

`templates/product.json` now uses the **page-2 format** (it was the weaker
original layout). On top of that:

1. **Buy-box trust bar** — new `snippets/tda-trust-bar.liquid`, rendered under
   the payment badges. Australian owned & operated / priced in AUD / tracked
   AusPost / lifetime replacement. Directly answers the "is this Australian,
   is this a scam" doubt above.
2. **Survey social proof** — new `sections/tda-voc-reasons.liquid`, placed
   after the Judge.me carousel. Shows the real 52% / 40% / 20% figures in
   customers' own words, with the sample size footnoted. The US competitor
   cannot copy this.
3. **Sticky add-to-cart** — new `sections/tda-sticky-atc.liquid`. It forwards
   the click to the real buy button rather than submitting its own form, so
   personalisation validation, the multi-pack logic and the frame upsell all
   keep working untouched.
4. **Objection-ordered FAQ tabs** — rebuilt to match measured objection
   frequency, including a new **"Is it worth the price?"** tab for the #1
   objection (17.8%), which the page had no answer for.
5. **Benefit bullets** — now lead with the #1 purchase driver in the
   customer's own words.
6. **Honest urgency** — replaced "Only 7 printing slots left this week" with
   "Order today — dispatched within 48 hours, Mon–Fri". Invented scarcity is
   the wrong play for an audience already asking "is this a scam", and
   unsubstantiated scarcity claims carry Australian Consumer Law risk.

### Refactor
The two large inline code blocks were moved out of the template into
`snippets/tda-pack-multi.liquid` and `snippets/tda-frame-upsell.liquid`
(plus `tda-bullets` and `tda-compare-table`). Behaviour is unchanged — both
were pure HTML/CSS/JS with no Liquid variables, and `{% render %}` emits them
in the same DOM position, preserving script order and the
`window.tdaGetPackCount` handshake between them.

Known cosmetic deltas vs the original bytes (verified by diff, no behaviour
change): a comment-banner character count, `'✕ Remove'` written as
`'✕ Remove'` (identical JS string), and two non-breaking spaces rendered as
normal spaces in the "How fast is shipping?" answer.

## Not done — these are deliberately your call

- **Price is untouched.** page-2 is live at **$69.99** (compare-at $115); the
  original is **$59.99** (compare-at $100). Price is a product-level field, so
  changing it would hit the live store immediately. Run the format test first,
  then price — changing both at once makes the result unreadable.
- **The pack is still described as 5 pages**, because it is. See below.

## Recommendation against the 10-page plan

When customers were asked what they would have paid extra for, **not one
asked for more pages**. 95 of 342 said they would not pay extra for anything.
What they would pay for is all presentation:

| Demand | Upgrade |
|---|---|
| ~75 | A premium leather-look folder |
| ~70 | Gold foil lettering on the folder |
| ~55 | A personal message page |
| ~35 | A linen-wrapped presentation box |
| — | Choice of paper / folder colour |

A **personal message page** is the standout: it is effectively a 6th page
customers will pay for, carries zero factual risk, and strengthens the gift
framing that 91.6% of buyers are here for. Doubling to 10 researched pages
doubles the factual-error surface on a product sold with a lifetime
replacement guarantee, for value customers did not ask for.

Highest-demand new products: Newspaper Broadsheet Print (43), Surname Archive
Pack (42), Wedding Anniversary Archive Pack (25), Leather-Bound Book (22).

## Fix the survey itself

Grapevine, last 180 days: 537 responses, 1,294 unique impressions,
28.9% response rate, **63.7% completion rate**, $45,744 attributed revenue.

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
| **What were you looking at before you found us?** | **387** | **−68** |
| Anything almost stopped you? | 374 | −13 |
| Other keepsake products? | 362 | −12 |
| Upgrades you'd pay extra for? | 342 | −20 |

The single worst drop is the **open-text** question — typing costs far more
effort than tapping, and the answers are mostly "Nothing" and "Facebook",
so it is buying very little. Two changes:

1. Convert it to multiple choice (Facebook / Instagram / Google / nothing in
   particular / something else), or move it to last.
2. Move the two commercially valuable questions (upgrades, other products)
   **earlier** — they currently sit where drop-off is worst, which is why they
   have the smallest samples.

## Before publishing

The theme is unpublished, so nothing here is live. Preview it and check:
- Add to cart works for 1 pack, and for 2+ packs (the free $20 gift card path).
- The frame upsell and its quantity picker still work.
- The sticky bar appears on scroll and its button adds to cart on mobile.
- The product page renders (this template carries both Shopify's auto-generated
  banner comment and the build banner above the JSON).
