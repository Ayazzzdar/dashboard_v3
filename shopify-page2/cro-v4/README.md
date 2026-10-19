# CRO v4 theme — gift card ladder

Live in the unpublished theme **CRO v4 — Page-2 Format + Trust Stack (2026-10-14)**
(`gid://shopify/OnlineStoreTheme/159801344155`) only. The published theme and the
page-2 test are untouched.

## The offer

| Cart | Gift card | Shipping |
|---|---|---|
| 1 archive ($59.99) | FREE $20, shown as included from page load | $10 (under the $80 threshold) |
| 2 archives ($119.98) | upgraded to FREE $25 | free (over $80) |

## Moving parts

| Piece | Where | ID |
|---|---|---|
| Archive | product / variant | 8963699769499 / 48204546932891 |
| Gift Card $20 | variant | 49514465558683 |
| Gift Card $25 | variant (created 19 Oct) | 49852343779483 |
| Frame your order™ | variant | 48940258918555 |
| "CRO v4 - FREE $20 Gift Card with 1 Archive" | automatic discount | DiscountAutomaticNode/1233313267867 |
| "CRO v4 - FREE $25 Gift Card with 2 Archives" | automatic discount | DiscountAutomaticNode/1233313300635 |

Both discounts are Buy X Get Y at 100% off, one use per order, and combine with
product, order and shipping discounts so free shipping still applies.

## Theme files

- `snippets/tda-pack-multi.liquid` — the offer UI and the add-to-cart chain
- `snippets/tda-giftcard-guard.liquid` — keeps the bonus card matched to the cart
- `sections/footer-group.json` — renders the guard on every page of the theme

`snippets/tda-frame-upsell.liquid` is unchanged.

## How the cart stays correct

The add-to-cart intercept only takes over when the request is adding an archive,
so the gift card and frame requests pass straight through and can never trigger a
second card. The guard then watches every cart mutation: it removes the bonus card
if the cart drops to zero archives, swaps $25 for $20 when the cart drops to one,
swaps $20 for $25 when it reaches two, and resets the quantity if it ever exceeds
one. It only touches a gift card line carrying `properties[_Bonus]`, so a card the
shopper chose to buy is left alone.

## Test

```
node shopify-page2/test/run-cro-v4.mjs
```

Nine scenarios against a simulated Shopify cart, driving the real snippets in
headless Chromium in the live block order. All passing as of the last run.

## Known exposure

The discounts are store-wide, as all Shopify discounts are. On the published theme
a shopper who manually adds a $20 or $25 gift card to a cart containing an archive
would get it free. Narrow this by moving the bonus to its own hidden gift card
product if the test runs long or goes to the live theme.
