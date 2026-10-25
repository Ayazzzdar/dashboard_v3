# The Day Archive — Klaviyo Email Playbook & Handover

**Purpose:** complete working context for running Klaviyo email marketing for The Day Archive.
Hand this file to a local agent/session so it can pick up without re-discovering anything.

**Last verified against live Klaviyo + Shopify data:** 26 Oct 2026 (AEDT).
All performance figures below are pulled from the Klaviyo reporting API over
**last_30_days** unless stated otherwise. Re-pull before relying on them.

---

## 1. Business snapshot

The Day Archive sells personalised keepsake packs built around **one specific date** —
real Australian newspaper front pages plus contextual pages (prices, names, culture,
economy) for that day. Australian store, AUD, Shopify + Klaviyo + Judge.me.

| Metric | Value |
|---|---|
| Revenue, week 5–11 Oct | $9,032 / 136 orders |
| Revenue, week 12–18 Oct | $10,643 / 156 orders (+17.8%) |
| Run rate since | ~20–25 orders/day |
| Normal daily sessions | 650–840 at 3.2–4.6% CVR |
| **Email share of revenue** | **~6%** |

**Email is a small lever on this business.** In the week of 5–11 Oct, four campaigns
produced 8 orders / $556 against $9,032 total revenue. Do not expect campaigns to close
a double-digit revenue gap — when revenue drops, check traffic and conversion rate first.
The 10 Oct dip was a traffic-quality event: 1,760 sessions at 0.97% CVR versus a normal
650–840 at 3.2–4.6%.

### Last 30 days, all email campaigns combined
- 30,771 recipients → 42 orders → **$3,955.63**
- **249 unsubscribes** to earn that $3,956

That unsubscribe-to-revenue ratio is the central strategic problem. See §10.

---

## 2. Products & pricing

| Product | Price | Notes |
|---|---|---|
| Birth Day Archive Pack | $59.99 | + $10 shipping. The core product. |
| Birth Day Archive Pack™ (unlisted) | $69.99 | Unlisted variant |
| Frame add-on | $40 listed / $30 unlisted | |
| Gift Card | $20–$250 | |
| **The Day You Passed Archive** | $59.99 | Memorial product, launched 21 Oct 2026 |

Product URL pattern: `https://thedayarchive.com/products/<handle>`
e.g. `https://thedayarchive.com/products/the-day-you-passed-archive`

---

## 3. HARD RULES — do not break these

These come directly from the store owner. Several were corrections to earlier mistakes.
Treat them as non-negotiable and check every draft against them.

1. **Never claim a discount link auto-applies.** The link does NOT apply the code.
   Always write: *"Type it into the discount box at checkout."*
2. **No reply-driven CTAs.** Never invite customers to reply to look up dates, ask
   questions, or "start a conversation". The owner will not be answering.
3. **Never reply to complaint threads.** Complaints get added to the exclusion list
   only. Owner's words: *"no dont reply just exclude them also"*
4. **Do not exclude customers who were unhappy about shipping time but happy once it
   arrived.** Only unresolved/damaged complaints go on the exclusion list.
5. **Birthday framing only, for the birthday product.** No wedding, anniversary, or
   generic "special occasion" framing: *"the date is specific to a birthday so dont go
   mentioned wedding etc it is tailor to that"*
6. **Omit all dispatch/delivery timings.** No "ships in X days", no "arrives by".
7. **Never fabricate reviews or customer quotes.** Verbatim real reviews only — see §13
   for the verified set and the screening script.
8. **Opens are not driven by email content.** Owner's correction: *"the open rate is not
   dictated by the internals of the email people cant see it"*. Subject line, sender and
   send time drive opens. Never claim a design change improved opens.
9. **Campaigns are created as Draft and handed over.** Do not fire a 2,000+ recipient
   send without an explicit go-ahead.
10. **Owner's email (ayazdar2@gmail.com) is for identification only.** Never send it to
    an unrelated service.

---

## 4. Account ID reference

### Klaviyo
| Thing | ID |
|---|---|
| Company / CDN prefix | `XHG2Ry` |
| **Segment: Delivered Confirmed OR Ordered 20+ Days Ago** ("Delivered Buyers") | `VybnyR` |
| **Segment: Non Buyers** | `WypXLV` |
| Segment: All Buyers Total | `ShE3m6` |
| **List: Exclude — Damaged Item / Unresolved Complaint** | `QZTa9D` |
| List: Popup signups | `SpCj39` |
| Popup form | `YgKWqJ` |
| Metric: **Placed Order** (use as conversion metric) | `W4vDTk` |
| Metric: Viewed Product (API/onsite) | `VkRkVj` |
| Metric: Checkout Started (Shopify) | `XdUuMc` |

Audience setup used on every campaign:
- `included`: `["VybnyR"]` and/or `["WypXLV"]`
- `excluded`: `["QZTa9D"]` (always). When sending only to buyers, also exclude `WypXLV`.

### Flows (all live, archived=false)
| Flow | ID | Trigger |
|---|---|---|
| Welcome Series — Popup Signups (WELCOME10) | `U33xiB` | Added to List |
| Browse Abandonment v2 — 3 Email | `VYThBZ` | Metric (Viewed Product) |
| OG Thank You / Welcome Series — New vs Returning Split | `WCBxyJ` | Metric |
| Page 2 - Thank You / Welcome Series | `WYZTBk` | Metric |
| Abandoned Checkout — 3-Email | `XDQvs4` | Metric |

Old browse abandonment draft `Rj9gkh` is archived. It had sat in draft since 24 Sep and
**never sent a single email** — worth remembering before trusting any claim that an
existing flow "isn't performing well".

### Klaviyo UI deep links
- Campaign: `https://www.klaviyo.com/campaign/{CAMPAIGN_ID}/wizard`
- Flow: `https://www.klaviyo.com/flow/{FLOW_ID}/edit`
- Template: `https://www.klaviyo.com/email-editor/{TEMPLATE_ID}/edit`
- Segment/List: `https://www.klaviyo.com/lists/{ID}`

---

## 5. Shopify discount codes — live state

| Code | % | Status | Uses | Expiry | Notes |
|---|---|---|---|---|---|
| `WELCOME10` | 10 | ACTIVE | 350 | none | Popup welcome offer — intentional, leave alone |
| `FRONTPAGE10` | 10 | ACTIVE | 0 | none | Browse abandonment flow code |
| **`10OFF`** | 10 | ACTIVE | **10** | **none** | ⚠️ leaking, no expiry |
| **`20OFF`** | 20 | ACTIVE | 1 | **none** | ⚠️ leaking, no expiry |
| **`THANKYOU5`** | 5 | ACTIVE | 4 | **none** | ⚠️ leaking, no expiry |
| **`10SHIP`** | 10 | ACTIVE | 0 | **none** | ⚠️ no expiry |
| **`DAVID`** | 10 | ACTIVE | 0 | **none** | ⚠️ no expiry |
| `GIFT20` / `XMAS20` | 20 | EXPIRED | 1 each | 18 Oct | |
| `XMAS25` | 25 | EXPIRED | 2 | 14 Oct | |
| `TODAY20` | 20 | EXPIRED | 1 | 10 Oct | |
| `TWODATES` | 20 | EXPIRED | 0 | 11 Oct | |
| `WEEKEND15` | 15 | EXPIRED | 3 | 4 Oct | |
| `DAY20` | 20 | EXPIRED | 3 | 1 Oct | |
| `DATE20` | 20 | EXPIRED | 2 | 27 Sep | |

**Open item, raised repeatedly and never authorised:** expire `10OFF`, `20OFF`,
`THANKYOU5`, `10SHIP`, `DAVID`. `10OFF` has gone 1 → 9 → 10 redemptions across recent
weeks. These are open-ended discounts anyone can find and reuse.

`FRONTPAGE10` is permanently live because **flows cannot carry a code end date**. The
proper fix is Klaviyo dynamic coupons (per-profile unique codes with an expiry window).

### Shopify API notes
- `create-discount` requires `startsAt` **and** `customerEligibility: "all_customers"`.
- Use `discountCodeBasicUpdate` to set `appliesOncePerCustomer` or amend `startsAt`.
- `create-discount` has been blocked once by the auto-mode classifier as
  `[Real-World Transactions]`. It succeeded on a plain retry after an MCP reconnect.
- ShopifyQL: the `sales` dataset is **pre-aggregated**, so `sum()` is not a valid
  function and there is no `orders` table.
  Working form: `FROM sales SHOW net_sales, orders, average_order_value GROUP BY day SINCE -30d UNTIL today ORDER BY day`
  Also works: `FROM sessions SHOW sessions, conversion_rate GROUP BY day`

---

## 6. Brand assets

### Colour tokens
```
navy         #1c2a4e
gold         #c7a97a
gold-dark    #c1a370
cream        #faf6ec
page bg      #ddcfae
parchment    #f4ecda
card border  #e6dcc4
trust strip  #f0e7d2
ink          #2b2b2b
```
Typeface: **Georgia, serif** throughout.

### Hosted images (all verified live on Klaviyo CDN)
Base: `https://cdn.klaviyomail.com/company/XHG2Ry/images/`

| Asset | Filename |
|---|---|
| Logo (cream, for navy plaque) | `64ed16e5-d0e0-438b-9a2e-79d354626f98.png` |
| Transparent pack shot | `b2fe7250-f652-4b99-b8ed-e9de7c68e18f.png` |
| Paper tear, navy → cream | `4b8a57fa-e542-4e92-95cf-c0b208781ccc.png` |
| Paper tear, cream → navy | `21cc28ac-8ab4-4cd4-9120-b314f09f975f.png` |
| Tear divider | `b0ae6e9c-4d64-4d3a-b51c-21ba1b4638b7.png` |
| Paperclip | `3f1c8c41-c6ad-4e68-8691-1aeae1ed39ef.png` |
| Product hero (birthday pack) | `2f305823-4898-4656-924c-b8fcf2e11494.jpeg` |
| Day You Passed hero | `8557804a-7d00-4b9c-96aa-b7da6d7f4bc9.jpeg` |
| Day You Passed page 1 | `d68f95db-9d17-4534-9854-6e7d12f83377.jpeg` |
| Day You Passed pages 2–3 | `d823bc23-b70f-4347-9d4c-0db70eba1bff.jpeg` |
| Day You Passed pages 4–5 | `1b049ddd-dbba-4425-973f-22a72f9b5054.jpeg` |

**Uploading new images** — `upload_image_from_url` needs a `body` wrapper:
```json
{"data":{"type":"image","attributes":{
  "name":"...", "import_from_url":"https://...", "hidden":false}}}
```
It fetches server-side, so it works even when the sandbox proxy blocks the CDN.
It **rejects WebP by URL**. Data URIs are accepted.

**Note on the sandbox:** all external image CDNs (cdn.shopify.com, cdn.klaviyomail.com)
are proxy-blocked, so hosted images cannot be downloaded or previewed directly. To review
a build locally, swap CDN URLs for local placeholder files, then screenshot — see §7.

---

## 7. Email template architecture

### The proven shell (product-first)
Derived from `xmas20.html`. This became the base for nearly every email after 15 Oct.
Block order, top to bottom:

1. Navy header with cream logo plaque
2. Paper tear (navy → cream)
3. Gold-tabbed ribbon (short urgency/positioning line)
4. Headline — **product first**, not offer first
5. Hero image
6. **Primary CTA** — keep it high; do not bury it below a tall hero
7. Tear divider
8. Pack ribbon
9. Paperclipped white card: image + 4 gold ✓ bullets
10. Mid copy
11. Paper tear
12. Offer block (code + "Type it into the discount box at checkout")
13. Trust strip
14. Paper tear
15. Navy footer with `{% unsubscribe 'Unsubscribe' %}`

### Mobile stacking CSS (used in every build)
```css
@media only screen and (max-width:480px){
  .stack{display:block !important;width:100% !important;max-width:100% !important;}
  .stack-img{padding:0 0 16px 0 !important;text-align:center !important;}
  .stack-img img{margin:0 auto !important;}
  .big{font-size:48px !important;line-height:48px !important;}
  .pad{padding-left:18px !important;padding-right:18px !important;}
}
```

### Template lineage (scratchpad history)
`flash.html` → `flash2.html` (DAY20) → `weekend.html` / `weekend2.html` →
`final.html` (WEEKEND15 Final Hours) → `story.html` → `twodates.html` →
`today20.html` → `xmas.html` (XMAS25) → **`xmas20.html`** (the reusable base) →
`gift20.html` → `ba1/ba2/ba3.html` (browse flow) → `final20.html` → `proof.html` →
`dyp.html` → `dyp2.html`

### Derivation pattern — surgical block slicing with asserted replacement
Always assert before replacing so a silent no-op is impossible:
```python
OFFER_START = '  <tr><td align="center" class="pad" ...>Until Sunday</p>'
TRUST = '  <!-- TRUST -->'
s, e = h.index(OFFER_START), h.index(TRUST)
h = h[:s] + REPLACEMENT + h[e:]
for a, b in rep:
    assert a in h, 'MISSING: ' + a[:70]
    h = h.replace(a, b)
```

### Constraint check — run on every build before creating the template
```python
bad = [t for t in ['wedding','anniversar','dispatch','business days','% off','repl']
       if re.search(t, h, re.I)]
print('flagged:', bad,
      '| discount-box:', 'discount box at checkout' in h,
      '| unsub:', 'unsubscribe' in h)
```

### Local render harness
CDNs are proxy-blocked, so substitute local placeholders, then screenshot:
```python
m = {'4b8a57fa-...png':'t_nc.png', '21cc28ac-...png':'t_cn.png',
     'b0ae6e9c-...png':'t_div.png', '3f1c8c41-...png':'clip_ph.png',
     '2f305823-...jpeg':'ph_hero.png', 'b2fe7250-...png':'ph_pack.png',
     '64ed16e5-...png':'ph_pack.png'}
for k, v in m.items():
    h = h.replace('https://cdn.klaviyomail.com/company/XHG2Ry/images/' + k, v)
```
Then Playwright with `full_page=True` (a `clip` outside the viewport fails).
Chromium is pre-installed; launch with `--no-sandbox --disable-dev-shm-usage`.

---

## 8. Campaign history & results (last 30 days)

### To Delivered Buyers — segment `VybnyR`
| Campaign | Sent | Deliv | Open | Clicks | CTOR | Orders | Revenue | RPR | Unsub |
|---|---|---|---|---|---|---|---|---|---|
| DATE20 Final Hours | 27 Sep | 1,840 | 27.9% | 3 | 0.59% | 3 | $916.88 | **$0.498** | 16 |
| How Many Birthdays Are Left | 28 Sep | 1,851 | 30.4% | 0 | 0% | 0 | $0 | $0 | 19 |
| DAY20 — 24hr Flash | 30 Sep | 1,883 | 28.1% | 4 | 0.76% | 2 | $235.98 | $0.125 | 8 |
| WEEKEND15 — Weekend Offer | 2 Oct | 1,902 | 27.0% | 3 | 0.58% | 1 | $69.99 | $0.037 | 5 |
| WEEKEND15 — Final Hours | 4 Oct | 1,912 | 27.9% | 2 | 0.38% | 2 | $209.97 | $0.110 | 13 |
| What Was On The Front Page | 6 Oct | 1,943 | 33.6% | 8 | 1.23% | 2 | $159.98 | $0.082 | 26 |
| TWODATES — Two Packs | 8 Oct | 1,987 | 29.2% | 3 | 0.52% | 1 | $69.99 | $0.035 | 12 |
| TODAY20 — Today Only | 10 Oct | 2,016 | 26.4% | 4 | 0.75% | 2 | $139.98 | $0.069 | 13 |
| TODAY20 — Final Hour (11pm) | 10 Oct | 2,012 | 26.0% | 2 | 0.38% | 1 | $69.99 | $0.035 | 16 |
| XMAS25 — Early Bird | 12 Oct | 1,996 | 28.2% | 5 | 0.89% | 3 | $218.99 | $0.110 | 18 |
| GIFT20 — Product-First | 15 Oct | 2,026 | 26.9% | 3 | 0.55% | 4 | $301.98 | $0.149 | 11 |
| XMAS20 — Final Hours | 18 Oct | 2,060 | 27.3% | 3 | 0.53% | 1 | $119.98 | $0.058 | 19 |
| The Day You Passed — Launch | 21 Oct | 2,101 | **34.0%** | 6 | 0.84% | 2 | $133.99 | $0.064 | 19 |

### To Non Buyers — segment `WypXLV`
| Campaign | Sent | Deliv | Open | Clicks | Click % | CTOR | Orders | Revenue | RPR | Unsub |
|---|---|---|---|---|---|---|---|---|---|---|
| DAY20 — 24hr Flash | 30 Sep | 266 | 29.7% | 5 | **1.88%** | **6.33%** | 3 | $245.98 | **$0.925** | 4 |
| WEEKEND15 — Weekend | 2 Oct | 286 | 30.1% | 4 | 1.40% | 4.65% | 1 | $162.98 | $0.570 | 4 |
| WEEKEND15 — Final Hours | 4 Oct | 325 | 27.4% | 5 | 1.54% | 5.62% | 4 | $258.99 | $0.797 | 1 |
| What Was On The Front Page | 6 Oct | 364 | **37.9%** | 5 | 1.37% | 3.62% | 2 | $128.00 | $0.352 | 4 |
| TWODATES | 8 Oct | 391 | 30.2% | 1 | 0.26% | 0.85% | 0 | $0 | $0 | 8 |
| TODAY20 — Today Only | 10 Oct | 415 | 26.5% | 5 | 1.21% | 4.55% | 2 | $122.00 | $0.294 | 1 |
| TODAY20 — Final Hour (11pm) | 10 Oct | 421 | 27.1% | 0 | 0% | 0% | 0 | $0 | $0 | 2 |
| XMAS25 — Early Bird | 12 Oct | 458 | 30.6% | 5 | 1.09% | 3.57% | 2 | $133.99 | $0.293 | 4 |
| XMAS20 — Product-First | 15 Oct | 499 | 35.5% | 3 | 0.60% | 1.70% | 2 | $122.00 | $0.244 | 4 |
| XMAS20 — Final Hours | 18 Oct | 551 | 27.9% | 2 | 0.36% | 1.30% | 1 | $69.99 | $0.127 | 7 |
| Proof — No Discount | 19 Oct | 553 | 29.3% | 4 | 0.72% | 2.47% | **0** | **$0** | $0 | 9 |
| The Day You Passed | 24 Oct | 634 | 33.0% | 2 | 0.32% | 0.96% | 1 | $64.00 | $0.101 | 6 |

### 30-day audience aggregate — the single most important table here
| | Non Buyers | Delivered Buyers |
|---|---|---|
| Recipients | 5,182 | 25,589 |
| Open rate | 30.52% | 28.70% |
| Click rate | **0.79%** | 0.18% |
| CTOR | **2.60%** | 0.63% |
| Conversion rate | **0.33%** | 0.09% |
| **Revenue per recipient** | **$0.2533** | $0.1037 |
| AOV | $72.66 | $110.32 |
| Unsubscribes | 54 (1.05%) | **195** (0.76%) |
| Revenue | $1,307.93 | $2,647.70 |

Non Buyers convert at **~3.7× the rate** and return **~2.4× the revenue per recipient**,
on one fifth the volume. Delivered Buyers generated **195 of the 249 unsubscribes**.

---

## 9. Flow inventory & results (last 30 days)

| Flow | Recip | Open | Click | CTOR | Orders | Revenue | **RPR** |
|---|---|---|---|---|---|---|---|
| **Welcome Series — Popup (`U33xiB`)** | 1,476 | 33.0% | 3.14% | 9.50% | 29 | **$2,345.85** | **$1.601** |
| **Abandoned Checkout (`XDQvs4`)** | 30 | 29.6% | 11.11% | 37.5% | 2 | $128.00 | **$4.741** |
| Page 2 Thank You (`WYZTBk`) | 126 | 44.8% | 0% | 0% | 1 | $64.00 | $0.512 |
| Browse Abandonment v2 (`VYThBZ`) | 97 | 34.0% | 5.15% | 15.2% | 0 | $0 | $0 |
| OG Thank You (`WCBxyJ`) | 1,591 | **52.1%** | 1.07% | 2.05% | 1 | $89.99 | $0.057 |

### Per-email detail on the two that matter

**Welcome Series `U33xiB` — the money machine**
| Email | ID | Recip | Open | Click | CTOR | Orders | RPR |
|---|---|---|---|---|---|---|---|
| Welcome 1 — Birthday explicit | `Tq2uFY` | 674 | 37.8% | 4.35% | 11.51% | 22 | **$2.718** |
| Welcome 2 — What they'll unwrap | `WYSfGW` | 427 | 28.9% | 3.05% | 10.57% | 5 | $0.897 |
| Welcome 3 — Nobody kept the paper | `Yah6AN` | 375 | 29.2% | 1.07% | 3.67% | 2 | $0.413 |

**Browse Abandonment v2 `VYThBZ` — now LIVE** (built 16 Oct, went live, first data in)
| Email | ID | Recip | Open | Click | CTOR | Orders |
|---|---|---|---|---|---|---|
| Email 1 — 1 hr | `RM2tYq` | 45 | 46.7% | **11.11%** | **23.81%** | 0 |
| Email 2 — 24 hrs | `YjGXpH` | 7 | 14.3% | 0% | 0% | 0 |
| Email 3 — 3 days, 10% off | `VheYDY` | 45 | 24.4% | 0% | 0% | 0 |

Flow config: trigger Viewed Product (`VkRkVj`); 1 hr → E1, +23 hr → E2, +2 days → E3
(10% `FRONTPAGE10`, 24 hr); exits on Placed Order or Checkout Started; 30-day re-entry;
smart sending on. Trigger volume is ~150–270 identified profiles/week.

**Two things stand out and are worth acting on:**
1. **Email 1 clicks at 11.11% / 23.81% CTOR** — the best click engagement anywhere in the
   account. Email 3 clicks at 0%. The 10%-off final email is the weak one; the immediate
   reminder is the strong one.
2. **Abandoned Checkout only reached 30 recipients in 30 days** while returning the
   highest RPR in the account ($4.74). For a store doing 20–25 orders/day, 30 abandoned
   checkout emails looks far too low. Worth auditing the trigger/filters — this is
   probably the largest unclaimed revenue in the account.

---

## 10. What we have actually learned

Ordered by how much evidence supports it.

### 1. Audience beats creative, by a wide margin
Non Buyers return 2.4× the revenue per recipient of Delivered Buyers and 3.7× the
conversion rate. Every creative experiment has moved metrics by fractions of a percent;
switching audience moves them by multiples.

### 2. Discount depth is not the lever
15% → 6 orders. 20% → 2. 25% → 2. Across four discounted sends (15–18 Oct) there were
**4 code redemptions total** against ~2,500 emails each. Deeper discounts did not buy
more orders. Klaviyo also over-credits: XMAS25 was credited 4 orders but Shopify showed
only 2 code redemptions (~$58 of genuinely code-driven revenue, not $128).

### 3. Late-evening sends fail
Two "final hours" sends at 11:02pm and 10:35pm produced 2 clicks/17 unsubs and
4 clicks/20 unsubs. The 11pm TODAY20 Final Hour got **zero clicks** from 421 Non Buyers.
Midday sends consistently outperform. Stop sending late at night.

### 4. Opens and clicks are not the constraint — landing conversion is
- The Proof email achieved a strong 2.47% CTOR and **zero orders**.
- The Day You Passed hit 33–34% opens, the best of the month, and 0.84–0.96% CTOR.
- Browse Abandonment Email 1 clicks at 11% and has produced zero orders.

People are opening and clicking. They are not buying once they land. Further email
creative iteration has a low ceiling until that changes.

### 5. A CTA-position fix did not work — stated plainly
For the Day You Passed follow-up the hypothesis was that a buried CTA caused low clicks.
The email was tightened specifically for that: hero 420px → 340px, 9 images → 7,
6 bullets → 4, spread row removed. Result: CTOR moved 0.84% → 0.96% on 209 opens, which
is inside noise. **The CTA-position hypothesis is not supported.** What did hold was the
subject line (33–34% opens across both audiences) and the Non Buyers RPR edge.

### 6. The Day You Passed does not work on Non Buyers
Non Buyers click at 1.2–1.9% on birthday-pack flash offers and at **0.32%** on the
memorial product — a 4–6× drop. High opens were curiosity about the subject line. Cold
prospects want the birthday pack; the memorial product needs a different, warmer context.

### 7. Flows beat campaigns by 1–2 orders of magnitude
Welcome Series returns **$1.60/recipient** and Abandoned Checkout **$4.74**, against
$0.03–0.50 for campaigns. Any hour spent on flow coverage and triggering is worth more
than an hour spent on the next campaign.

### 8. The unsubscribe cost is real
249 unsubscribes bought $3,956 in 30 days, 195 of them from Delivered Buyers who
convert at 0.09%. The buyer list is being burned down at roughly 0.76% per send for
very little return. Reducing send frequency to that segment is a defensible move.

---

## 11. Playbook — building and shipping a campaign

### Recommended next campaign, based on the data above
The strongest single campaign of the month was **DAY20 — 24hr Flash (30 Sep)**:
2,157 recipients → 5 orders → $481.96, with the best Non Buyers numbers ever recorded
(1.88% click, 6.33% CTOR, $0.925/recipient). Replicate that pattern:

- **Product:** Birth Day Archive Pack (not the memorial product)
- **Offer:** 20% off, hard 24-hour window, fresh single-use code
- **Audience:** both segments, or Non Buyers only if protecting the buyer list
- **Send time:** midday AEDT. Never late evening.
- **Subject:** curiosity-led and specific. The two best open rates of the month came from
  concrete curiosity ("What Was On The Front Page" 37.9%, "The Day You Passed" 34.0%).
  A specific real detail beats an offer in the subject line.
- **Body:** the §7 product-first shell, CTA high, offer block last.

### Step-by-step
1. **Create the discount in Shopify** — `create-discount` with `percentage`,
   `startsAt` (now), `endsAt` (+24h), `customerEligibility: "all_customers"`.
   Then `discountCodeBasicUpdate` to set `appliesOncePerCustomer: true`.
2. **Build the HTML** from `xmas20.html` using the asserted-replacement pattern (§7).
3. **Run the constraint check** (§7). Confirm: no flagged terms, the phrase
   "discount box at checkout" present, unsubscribe tag present.
4. **Render and eyeball it locally** via the placeholder harness + Playwright.
5. **`create_email_template`** — `editor_type: "CODE"`, full `<html>`/`<body>`.
6. **`create_campaign`** — audiences `included` + `excluded` (always exclude `QZTa9D`),
   message `definition.channel: "email"`, with `subject`, `preview_text`, `from_email`,
   `from_label`.
7. **`assign_template_to_campaign_message`** using the message ID from step 6.
8. **`refresh_campaign_recipient_estimation`** then `get_campaign_recipient_estimation`
   to confirm the audience size.
9. **Leave it as Draft. Hand over the campaign URL.** Do not send.

### Reading results afterwards
Wait for the window to close before judging. A premature "0 orders" call was made on
XMAS20 Final Hours that later matured to 2 orders / $189.97 / AOV $94.99. Conversions
land late — give it at least a full day.

---

## 12. Klaviyo API gotchas

Each of these cost a failed call at least once.

- **Every MCP tool requires a `model` param.**
- **`get_campaign_report` / `get_flow_report` take FLAT params**, not a `body`:
  `statistics`, `value_statistics`, `conversion_metric_id`, `timeframe`, `filters`,
  `group_by`, `group_by_audience`.
- **`filters` is a raw string, not a JSON array:**
  `equals(campaign_id,"...")` or `contains-any(campaign_id,["a","b"])`.
  Passing an array returns "Could not parse filters".
- **`conversion_value`, `revenue_per_recipient`, `average_order_value` belong in
  `value_statistics`**, not `statistics` — otherwise literal_error.
- **`group_by_audience: true`** returns an extra `audience_aggregation` block. This
  produced the single biggest insight in this account. Use it.
- **Assigning a template to a campaign message CLONES the template.** The clone gets a
  new ID and is **not reachable via the templates API** (404). Keep the master template
  and edit that.
- **`update_flow` only changes status** (`draft` / `manual` / `live`). It cannot alter a
  flow definition.
- **`update_flow_action` CAN change a flow message's `template_id`**, and doing so
  **re-clones from the master at that moment**. That is the supported way to push an
  edited template into a live flow: update the master, then re-point the action at it.
  (Verified: master updated at 09:06:03, clone created 09:06:13.)
- **`create_flow`** uses `temporary_id` for new actions, linked via `links.next`;
  `entry_action_id` points at the first temp id.
- **Use `fields_template` / `fields_campaign` / `fields_campaign_message`** to limit
  responses. Without them, responses echo full HTML and burn enormous context.
- **`get_flow` with `fields_flow_action: ["definition.data.message.name"]` fails**
  ("not a nested object on the 'flow-action' resource"). Use
  `additional_fields_flow: ["definition"]` instead.
- **`query_metric_aggregates`** takes a `body` wrapper; `interval` enum is
  `day`/`hour`/`week`/`month`.
- Oversized GraphQL/MCP responses get written to a file under
  `~/.claude/projects/.../tool-results/`. Parse with `jq`, and run any Python that reads
  untrusted output with `python3 -I`.

---

## 13. Verified customer reviews

Judge.me data lives in Shopify **product metafields, namespace `judgeme`**:
- `review_widget_json_ld` — JSON-LD with `aggregateRating` and up to 32 `review` objects
- `reviews.rating`, `reviews.rating_count`

**Rule: quotes must be verbatim, and must not mention delivery.** Three otherwise-good
reviews were screened out for praising shipping speed (rule §3.6). The verification
script that enforces both:

```python
QUOTES = [
  (29, "All the little things from that year, the cost of a loaf of bread, ...", True),
  (10, "Ordered this for my twins 21st birthday and they loved it. ...", False),
  (19, "Fantastic gift for the person who has everything. ...", False),
]
for i, q, trimmed in QUOTES:
    assert q in body(i), f'NOT VERBATIM in review #{i}'
    assert not re.search(r'ship|arriv|deliver|quick|fast|post', q, re.I), \
        f'delivery mention in #{i}'
```

Always re-pull the live metafield and re-assert before using a quote. Never paraphrase,
never compose a quote, never attribute one to a named customer who did not write it.

---

## 14. Open items / backlog

Ordered by expected value.

1. **Audit the Abandoned Checkout flow trigger (`XDQvs4`).** 30 recipients in 30 days at
   $4.74/recipient for a store doing 20–25 orders/day. If the trigger is under-firing,
   this is the biggest unclaimed revenue in the account.
2. **Fix Browse Abandonment Email 3 (`VheYDY`).** 45 recipients, 24% open, 0% click. The
   10%-off final email is the dead one while Email 1 clicks at 11%. Rework or cut it.
3. **Expire the leaking codes:** `10OFF` (10 uses), `20OFF`, `THANKYOU5`, `10SHIP`,
   `DAVID` — all ACTIVE with no end date. Raised repeatedly, never authorised.
4. **Move `FRONTPAGE10` to Klaviyo dynamic coupons** so the flow code can carry an expiry.
5. **Investigate landing conversion.** Opens and clicks are healthy; orders are not.
   This is the real ceiling (§10.4) and it is not an email problem.
6. **Rewrite or cut Welcome 3 (`Yah6AN`)** — 375 recipients, 1.07% click, 2 orders,
   against Welcome 1's 4.35% click and 22 orders.
7. **Reduce send frequency to Delivered Buyers.** 195 unsubscribes in 30 days at 0.09%
   conversion.
8. **Verify the ™ product variant issue on flow `WCBxyJ`.**
9. **Day You Passed follow-up to openers-who-didn't-click** (~715 buyers). Requires a new
   Klaviyo segment on Opened Email AND NOT Clicked. Warmest identified audience available —
   but note §10.6 before re-pitching this product cold.

---

## 15. Tone and copy guidance

What the brand sounds like, drawn from what has worked:

- **Concrete over emotive.** The best-performing hooks name a real thing: a front page,
  the cost of a loaf of bread, the names that were popular that year. Specific detail is
  the product; abstractions about "memories" are not.
- **Product first, offer last.** The §7 shell puts the thing before the deal. Offer-first
  framing has not outperformed it.
- **Short sentences. Restrained punctuation. No exclamation marks.** Georgia serif,
  navy and gold, newspaper restraint.
- **Subject lines carry curiosity, not discounts.** The two best open rates of the month
  were curiosity hooks, not percentages.
- **Never oversell the memorial product.** It is a sincere product for a sincere moment;
  it does not take urgency framing or flash-sale language.
