/**
 * Mockup: gift card ladder on page-2 — $20 card with one archive, upgraded to
 * $25 + free shipping with a second. Structure mirrors the live page: bullets,
 * personalisation fields, Add-a-2nd-Archive button, reward row, Add to cart,
 * frame upsell, trust row. No totals panel.
 *
 * Run: node shopify-page2/preview/mockup.mjs [out.png]
 */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require(require('node:path').join(require('node:child_process').execSync('npm root -g').toString().trim(), 'playwright'));

const card = (amount) => 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(
  `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 112 70"><rect width="112" height="70" rx="5" fill="#16243a"/><rect x="5" y="5" width="102" height="60" rx="3" fill="none" stroke="#C9A24B" stroke-opacity=".7"/><text x="56" y="27" font-family="Georgia,serif" font-size="8" fill="#EDE6D6" text-anchor="middle" letter-spacing="1.4">THE DAY ARCHIVE</text><text x="56" y="50" font-family="Georgia,serif" font-size="17" font-weight="bold" fill="#C9A24B" text-anchor="middle">$${amount}</text></svg>`);

const css = `
  *{box-sizing:border-box}
  body{margin:0;background:#EEF0F4;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#1E3A5F}
  .sheet{display:flex;gap:26px;padding:26px;align-items:flex-start}
  .col{width:430px}
  .hdr{display:flex;align-items:center;gap:8px;margin:0 0 10px}
  .step{width:22px;height:22px;border-radius:50%;background:#1E3A5F;color:#fff;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0}
  .hdr h2{font-size:15px;margin:0;font-weight:700;white-space:nowrap}
  .hdr span{font-size:12px;color:#6B7585}
  .screen{background:#fff;border-radius:14px;padding:18px;box-shadow:0 2px 14px rgba(20,32,54,.10)}

  /* bullets, as on the live page */
  .bul{display:flex;align-items:center;gap:12px;margin-bottom:9px}
  .bul i{width:30px;height:30px;border-radius:50%;background:#EFF0F5;display:flex;align-items:center;justify-content:center;font-size:14px;font-style:normal;flex-shrink:0}
  .bul span{font-size:13.5px}
  .rule{height:1px;background:#EDEFF3;margin:14px 0}

  .lbl{display:block;font-size:13px;font-weight:700;margin-bottom:5px}
  .inp{width:100%;padding:11px 13px;border:1px solid #E2E7EE;border-radius:6px;font-size:15px;color:#1E3A5F;background:#fff;margin-bottom:10px}
  .inp.ph{color:#B0BCCF}

  .pack{background:#EFF0F5;border:1.5px solid #1E3A5F;border-radius:8px;padding:12px 14px;margin-bottom:10px}
  .pack-hdr{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}
  .pack-num{font-size:11px;font-weight:700;letter-spacing:.07em;text-transform:uppercase;opacity:.55}
  .pack-rm{font-size:12px;color:#C72329;font-weight:600}

  .add{display:flex;align-items:center;gap:10px;width:100%;padding:12px 14px;background:transparent;border:1.5px dashed #1E3A5F;border-radius:8px;text-align:left}
  .add-c{width:26px;height:26px;background:#1E3A5F;border-radius:50%;display:flex;align-items:center;justify-content:center;color:#fff;font-size:18px;font-weight:300;flex-shrink:0}
  .add-t{flex:1}
  .add-title{font-size:14px;font-weight:700;display:block;margin-bottom:1px}
  .add-sub{font-size:11px;opacity:.6;display:block}
  .add-sub b{font-weight:700;opacity:1}
  .badge{display:flex;flex-direction:column;align-items:center;gap:2px;background:#1E3A5F;color:#fff;font-size:9px;font-weight:700;padding:5px 8px;border-radius:3px;letter-spacing:.04em;line-height:1.25;text-align:center;flex-shrink:0;white-space:nowrap}

  .rw{display:flex;align-items:center;gap:10px;margin-top:8px;padding:9px 12px;border-radius:8px;border:1.5px solid #1E3A5F;background:#EFF0F5}
  .rw img{width:56px;height:auto;max-height:40px;object-fit:contain;flex-shrink:0}
  .mark{width:18px;height:18px;border-radius:50%;background:#EF9F27;color:#1E3A5F;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0}
  .rw-t{flex:1;min-width:0}
  .rw-title{display:block;font-size:13px;font-weight:700;line-height:1.25}
  .rw-sub{display:block;font-size:11px;opacity:.75;line-height:1.35;margin-top:1px}
  .rw-p{display:flex;flex-direction:column;align-items:flex-end;flex-shrink:0;line-height:1.1}
  .was{font-size:11px;text-decoration:line-through;opacity:.6}
  .now{font-size:14px;font-weight:700}
  .st{font-size:9px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;margin-top:2px;opacity:.75}
  .st.up{color:#C72329;opacity:1}

  .atc{width:100%;margin-top:14px;padding:16px;border:0;border-radius:10px;background:#1E3A5F;color:#fff;font-weight:700;font-size:16px;text-align:center}

  /* frame upsell, unchanged on the live page */
  .frame{position:relative;margin-top:16px;padding:10px;background:#EFF0F5;border:1.5px solid #1E3A5F;border-radius:8px;display:flex;align-items:center;gap:14px}
  .pop{position:absolute;top:-11px;right:16px;background:#1E3A5F;color:#fff;font-size:10px;font-weight:700;padding:3px 10px;border-radius:4px;letter-spacing:.5px}
  .cb{width:24px;height:24px;border:2.5px solid #1E3A5F;border-radius:5px;background:#fff;flex-shrink:0}
  .fr-t{flex:1}
  .fr-title{font-size:12px;font-weight:600;display:inline-block;margin-right:6px}
  .fr-off{display:inline-block;background:#1E3A5F;color:#fff;font-size:9px;font-weight:700;padding:2px 6px;border-radius:3px;letter-spacing:.3px;vertical-align:middle}
  .fr-d{font-size:11px;margin:4px 0 0}
  .fr-p{text-align:right;flex-shrink:0}
  .fr-p .m{font-size:16px;font-weight:700;white-space:nowrap}
  .fr-p .w{font-size:12px;text-decoration:line-through;opacity:.7}
  .fr-p .s{font-size:11px;font-weight:600}

  .trust{display:flex;align-items:center;justify-content:space-between;margin-top:18px;position:relative}
  .trust::before{content:"";position:absolute;left:20px;right:20px;top:20px;height:3px;background:#1E3A5F}
  .trust i{width:40px;height:40px;border-radius:50%;background:#1E3A5F;color:#fff;display:flex;align-items:center;justify-content:center;font-size:17px;font-style:normal;position:relative;z-index:1}

  .cap{margin:12px 2px 0;font-size:12.5px;color:#5A6575;line-height:1.5}
  .cap b{color:#1E3A5F}
`;

const bullets = `
  <div class="bul"><i>🇦🇺</i><span>Australian data — AFL, NRL, PMs and Economy stats</span></div>
  <div class="bul"><i>📖</i><span>Personalised 5-Page Birthdate Pack</span></div>
  <div class="bul"><i>🎁</i><span>Free Premium Gift Folder</span></div>
  <div class="bul"><i>🏅</i><span>Lifetime Replacement Guarantee</span></div>`;

const frame = `
  <div class="frame">
    <span class="pop">POPULAR</span>
    <span class="cb"></span>
    <span class="fr-t">
      <span class="fr-title">Add Premium Frame</span><span class="fr-off">25% OFF</span>
      <p class="fr-d">Add an extra touch to your gift — ready to display!</p>
    </span>
    <span class="fr-p"><span class="m">+$30.00</span><br><span class="w">$40.00</span><br><span class="s">Save $10.00</span></span>
  </div>
  <div class="trust"><i>🛒</i><i>🚚</i><i>🛍️</i></div>`;

const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>
<div class="sheet">

  <div class="col">
    <div class="hdr"><span class="step">1</span><h2>One archive</h2><span>— $20 card included</span></div>
    <div class="screen">
      ${bullets}
      <div class="rule"></div>
      <label class="lbl">Full Name for Personalisation *</label>
      <div class="inp">Jane Stafford</div>
      <label class="lbl">Birthday *</label>
      <div class="inp ph">DD/MM/YYYY</div>

      <div class="add">
        <span class="add-c">+</span>
        <span class="add-t">
          <span class="add-title">Add a 2nd Archive</span>
          <span class="add-sub">For someone else — upgrades to a <b>$25 gift card</b> + <b>free shipping</b></span>
        </span>
        <span class="badge"><span>+ $25 GIFT CARD</span><span>+ FREE SHIPPING</span></span>
      </div>

      <div class="rw">
        <img src="${card(20)}" alt="">
        <span class="mark">✓</span>
        <span class="rw-t">
          <span class="rw-title">+ FREE $20 Gift Card</span>
          <span class="rw-sub">Included with your order · emailed to you, no expiry</span>
        </span>
        <span class="rw-p"><span class="was">$20.00</span><span class="now">FREE</span><span class="st">Included</span></span>
      </div>

      <div class="atc">Add to cart</div>
      ${frame}
    </div>
    <p class="cap">The card is already theirs, so the page opens with a win. The 2nd archive now sells an <b>upgrade</b>, not an unlock.</p>
  </div>

  <div class="col">
    <div class="hdr"><span class="step">2</span><h2>Two archives</h2><span>— upgraded to $25 + free shipping</span></div>
    <div class="screen">
      ${bullets}
      <div class="rule"></div>
      <label class="lbl">Full Name for Personalisation *</label>
      <div class="inp">Jane Stafford</div>
      <label class="lbl">Birthday *</label>
      <div class="inp">14/03/1965</div>

      <div class="pack">
        <div class="pack-hdr"><span class="pack-num">Archive 2</span><span class="pack-rm">✕ Remove</span></div>
        <label class="lbl">Full Name for Personalisation *</label>
        <div class="inp">Tom Stafford</div>
        <label class="lbl">Birthday *</label>
        <div class="inp">02/11/1968</div>
      </div>

      <div class="add">
        <span class="add-c">+</span>
        <span class="add-t">
          <span class="add-title">Add a 3rd Archive</span>
          <span class="add-sub">For someone else — personalised separately</span>
        </span>
      </div>

      <div class="rw">
        <img src="${card(25)}" alt="">
        <span class="mark">✓</span>
        <span class="rw-t">
          <span class="rw-title">+ FREE $25 Gift Card</span>
          <span class="rw-sub">Upgraded — free shipping unlocked too · no expiry</span>
        </span>
        <span class="rw-p"><span class="was">$25.00</span><span class="now">FREE</span><span class="st up">Upgraded</span></span>
      </div>

      <div class="atc">Add to cart</div>
      ${frame}
    </div>
    <p class="cap">Same single row as now — it just swaps to <b>$25</b> and says free shipping came with it. No totals panel, nothing new under the button.</p>
  </div>

</div></body></html>`;

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 960, height: 1200 }, deviceScaleFactor: 2 });
await p.setContent(html, { waitUntil: 'load' });
const out = process.argv[2] || 'mockup.png';
await p.locator('.sheet').screenshot({ path: out });
await b.close();
console.log('wrote', out);
