/**
 * Builds a side-by-side mockup PNG of the proposed page-2 offer change:
 * gift card included at 1 archive, free shipping unlocked at 2.
 * Run: node shopify-page2/preview/mockup.mjs
 */
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = require(require('node:path').join(require('node:child_process').execSync('npm root -g').toString().trim(), 'playwright'));

const gift = 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(
  '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 112 70"><rect width="112" height="70" rx="5" fill="#16243a"/><rect x="5" y="5" width="102" height="60" rx="3" fill="none" stroke="#C9A24B" stroke-opacity=".7"/><text x="56" y="28" font-family="Georgia,serif" font-size="9" fill="#EDE6D6" text-anchor="middle" letter-spacing="1.5">THE DAY ARCHIVE</text><text x="56" y="50" font-family="Georgia,serif" font-size="18" font-weight="bold" fill="#C9A24B" text-anchor="middle">$20</text></svg>');

const css = `
  *{box-sizing:border-box}
  body{margin:0;background:#EEF0F4;font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;color:#1E3A5F}
  .sheet{display:flex;gap:28px;padding:26px}
  .col{width:420px}
  .hdr{display:flex;align-items:center;gap:8px;margin:0 0 10px}
  .step{width:22px;height:22px;border-radius:50%;background:#1E3A5F;color:#fff;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center}
  .hdr h2{font-size:15px;margin:0;font-weight:700}
  .hdr span{font-size:12px;color:#6B7585}
  .screen{background:#fff;border-radius:14px;padding:16px;box-shadow:0 2px 14px rgba(20,32,54,.10)}
  .lbl{display:block;font-size:13px;font-weight:700;margin-bottom:5px}
  .inp{width:100%;padding:11px 13px;border:1px solid #D0D8E4;border-radius:6px;font-size:15px;color:#1E3A5F;background:#fff;margin-bottom:10px}
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
  .add-sub b{font-weight:700}
  .badge{display:flex;flex-direction:column;align-items:center;gap:2px;background:#1E3A5F;color:#fff;font-size:9px;font-weight:700;padding:5px 8px;border-radius:3px;letter-spacing:.04em;line-height:1.25;text-align:center;flex-shrink:0;white-space:nowrap}

  .rw{display:flex;align-items:center;gap:10px;margin-top:8px;padding:9px 12px;border-radius:8px;border:1.5px solid #E3E4E9;background:#F5F0E8}
  .rw.on{background:#EFF0F5;border-color:#1E3A5F}
  .rw img{width:56px;height:auto;max-height:40px;object-fit:contain;flex-shrink:0}
  .ico{width:30px;height:30px;border-radius:50%;display:flex;align-items:center;justify-content:center;flex-shrink:0;font-size:15px;background:#E8E3D6}
  .rw.on .ico{background:#EF9F27;color:#1E3A5F;font-weight:700}
  .mark{width:18px;height:18px;border-radius:50%;background:#EF9F27;color:#1E3A5F;font-size:12px;font-weight:700;display:flex;align-items:center;justify-content:center;flex-shrink:0}
  .mark.lock{background:none;color:#1E3A5F;opacity:.5;font-size:13px}
  .rw-t{flex:1;min-width:0}
  .rw-title{display:block;font-size:13px;font-weight:700;line-height:1.25}
  .rw-sub{display:block;font-size:11px;opacity:.75;line-height:1.35;margin-top:1px}
  .rw-p{display:flex;flex-direction:column;align-items:flex-end;flex-shrink:0;line-height:1.1}
  .was{font-size:11px;text-decoration:line-through;opacity:.6}
  .now{font-size:14px;font-weight:700}
  .st{font-size:9px;font-weight:700;letter-spacing:.05em;text-transform:uppercase;margin-top:2px;opacity:.75}

  .atc{width:100%;margin-top:14px;padding:15px;border:0;border-radius:6px;background:#1E3A5F;color:#fff;font-weight:700;font-size:15px;text-align:center}

  .tot{margin-top:12px;border-top:1px solid #E7EAEF;padding-top:10px;font-size:12.5px}
  .tot div{display:flex;justify-content:space-between;padding:2.5px 0}
  .tot .g{color:#2F7D4F}
  .tot .big{font-weight:700;font-size:14px;border-top:1px solid #E7EAEF;margin-top:5px;padding-top:7px}
  .cap{margin:12px 2px 0;font-size:12px;color:#5A6575;line-height:1.5}
  .cap b{color:#1E3A5F}
`;

const giftRow = (on) => `
  <div class="rw on">
    <img src="${gift}" alt="">
    <span class="mark">✓</span>
    <span class="rw-t">
      <span class="rw-title">+ FREE $20 Gift Card</span>
      <span class="rw-sub">Included with your order · emailed to you, no expiry</span>
    </span>
    <span class="rw-p"><span class="was">$20.00</span><span class="now">FREE</span><span class="st">Included</span></span>
  </div>`;

const shipRow = (on) => `
  <div class="rw ${on ? 'on' : ''}">
    <span class="ico">🚚</span>
    <span class="mark ${on ? '' : 'lock'}">${on ? '✓' : '🔒'}</span>
    <span class="rw-t">
      <span class="rw-title">${on ? 'FREE Shipping' : 'Free Shipping'}</span>
      <span class="rw-sub">${on ? 'Unlocked — 2 archives in your order' : 'Add a 2nd archive to unlock · saves $10'}</span>
    </span>
    <span class="rw-p"><span class="was">$10.00</span><span class="now">${on ? 'FREE' : '$10.00'}</span><span class="st">${on ? 'Unlocked' : 'Locked'}</span></span>
  </div>`;

const html = `<!doctype html><html><head><meta charset="utf-8"><style>${css}</style></head><body>
<div class="sheet">

  <div class="col">
    <div class="hdr"><span class="step">1</span><h2>One archive</h2><span>— gift card included, shipping still $10</span></div>
    <div class="screen">
      <label class="lbl">Full Name for Personalisation *</label>
      <div class="inp">Jane Stafford</div>
      <label class="lbl">Birthday *</label>
      <div class="inp">14/03/1965</div>

      <div class="add">
        <span class="add-c">+</span>
        <span class="add-t">
          <span class="add-title">Add a 2nd Archive</span>
          <span class="add-sub">For someone else — unlocks <b>FREE shipping</b>, save $10</span>
        </span>
        <span class="badge"><span>+ FREE</span><span>SHIPPING</span></span>
      </div>

      ${giftRow(true)}
      ${shipRow(false)}

      <div class="atc">ADD TO CART</div>

      <div class="tot">
        <div><span>1 × Birth Day Archive Pack</span><span>$69.99</span></div>
        <div><span>Gift Card $20</span><span class="g">FREE</span></div>
        <div><span>Shipping</span><span>$10.00</span></div>
        <div class="big"><span>Total</span><span>$79.99</span></div>
      </div>
    </div>
    <p class="cap">Everyone gets the $20 card. The <b>$10 shipping</b> is what the 2nd archive now buys away.</p>
  </div>

  <div class="col">
    <div class="hdr"><span class="step">2</span><h2>Two archives</h2><span>— gift card + free shipping</span></div>
    <div class="screen">
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

      ${giftRow(true)}
      ${shipRow(true)}

      <div class="atc">ADD TO CART</div>

      <div class="tot">
        <div><span>2 × Birth Day Archive Pack</span><span>$139.98</span></div>
        <div><span>Gift Card $20</span><span class="g">FREE</span></div>
        <div><span>Shipping</span><span class="g">FREE</span></div>
        <div class="big"><span>Total</span><span>$139.98</span></div>
      </div>
    </div>
    <p class="cap">Both rows ticked. The second archive reads as <b>$10 saved now</b> rather than a locked gift.</p>
  </div>

</div></body></html>`;

const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 950, height: 1000 }, deviceScaleFactor: 2 });
await p.setContent(html, { waitUntil: 'load' });
const out = process.argv[2] || 'mockup.png';
await p.locator('.sheet').screenshot({ path: out });
await b.close();
console.log('wrote', out);
