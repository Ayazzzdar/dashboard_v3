/**
 * Headless test for the CRO v4 theme offer: $20 gift card with one archive,
 * upgraded to $25 with two or more, plus the cart guard.
 *
 * Mirrors the live CRO v4 block order (personalisation fields -> tda-pack-multi ->
 * buy buttons -> tda-frame-upsell) and simulates Shopify's cart endpoints, so the
 * real fetch-intercept chain is exercised end to end.
 *
 * Run: node shopify-page2/test/run-cro-v4.mjs
 */
import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
const require = createRequire(import.meta.url);
const { chromium } = (() => {
  try { return require('playwright'); } catch (e) {}
  const { execSync } = require('node:child_process');
  return require(require('node:path').join(execSync('npm root -g').toString().trim(), 'playwright'));
})();
import { createServer } from 'node:http';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const root = path.join(here, '..');
const strip = (s) => s.replace(/\{%-?\s*comment[\s\S]*?endcomment\s*-?%\}/g, '');
const block1 = strip(readFileSync(path.join(root, 'cro-v4', 'tda-pack-multi.liquid'), 'utf8'));
const guard  = strip(readFileSync(path.join(root, 'cro-v4', 'tda-giftcard-guard.liquid'), 'utf8'));
const block2 = readFileSync(path.join(here, 'frame-upsell-behaviour.html'), 'utf8');

const ARCHIVE = 48204546932891;
const GC20 = 49514465558683;
const GC25 = 49852343779483;
const FRAME = 48940258918555;

const page = `<!doctype html><html><head><meta charset="utf-8"><title>CRO v4 harness</title></head><body>
<form id="product-form">
  <label>Full Name <input name="properties[Full Name]" id="p1-name" value="Jane Stafford"></label>
  <label>Birthday <input name="properties[Birthday]" id="p1-bday" value="14/03/1965"></label>
  ${block1}
  <button type="button" id="atc">Add to cart</button>
  ${block2}
</form>
<script>
  document.getElementById('atc').addEventListener('click', async function(){
    const fd = new FormData();
    fd.append('id', '${ARCHIVE}');
    fd.append('quantity', '1');
    fd.append('properties[Full Name]', document.getElementById('p1-name').value);
    fd.append('properties[Birthday]', document.getElementById('p1-bday').value);
    const res = await fetch('/cart/add', { method: 'POST', body: fd });
    window.__lastStatus = res.status;
  });
</script>
${guard}
</body></html>`;

/* mini Shopify cart */
let cart, requests, nextKey, rejectGift = false;
function resetCart() { cart = []; requests = []; nextKey = 1; rejectGift = false; }
function addLine(fields) {
  const props = {};
  for (const k of Object.keys(fields)) {
    const m = k.match(/^properties\[(.+)\]$/);
    if (m) props[m[1]] = fields[k];
  }
  const same = cart.find((l) => l.variant_id === Number(fields.id) && JSON.stringify(l.properties) === JSON.stringify(props));
  if (same) { same.quantity += Number(fields.quantity || 1); return same; }
  const line = { key: String(nextKey++) + ':x', variant_id: Number(fields.id), quantity: Number(fields.quantity || 1), properties: props };
  cart.push(line);
  return line;
}

const server = createServer((req, res) => {
  let body = '';
  req.on('data', (c) => (body += c));
  req.on('end', () => {
    const url = req.url.split('?')[0];
    const json = (code, obj) => { res.writeHead(code, { 'Content-Type': 'application/json' }); res.end(JSON.stringify(obj)); };
    if (url === '/' || url === '/products/the-birth-day-archive-pack') { res.writeHead(200, { 'Content-Type': 'text/html' }); return res.end(page); }
    if (url === '/cart.js') return json(200, { items: cart, item_count: cart.reduce((n, l) => n + l.quantity, 0) });
    if (url === '/cart/add' || url === '/cart/add.js') {
      const ct = req.headers['content-type'] || '';
      let fields = {};
      if (ct.includes('multipart/form-data')) {
        const boundary = ct.split('boundary=')[1];
        for (const part of body.split('--' + boundary)) {
          const m = part.match(/name="([^"]+)"\r\n\r\n([\s\S]*?)\r\n$/);
          if (m) fields[m[1]] = m[2];
        }
      } else for (const [k, v] of new URLSearchParams(body)) fields[k] = v;
      requests.push({ url, fields });
      if (rejectGift && (fields.id === String(GC20) || fields.id === String(GC25))) {
        return json(422, { status: 422, message: 'Cannot find variant' });
      }
      return json(200, addLine(fields));
    }
    if (url === '/cart/change.js') {
      const { id, quantity } = JSON.parse(body);
      requests.push({ url, fields: { id, quantity } });
      const line = cart.find((l) => l.key === id);
      if (!line) return json(404, {});
      if (quantity === 0) cart = cart.filter((l) => l.key !== id); else line.quantity = quantity;
      return json(200, { items: cart });
    }
    res.writeHead(404); res.end();
  });
});

await new Promise((r) => server.listen(0, r));
const base = `http://127.0.0.1:${server.address().port}`;

const browser = await chromium.launch();
const ctx = await browser.newContext({ viewport: { width: 390, height: 844 } });
const pg = await ctx.newPage();
pg.on('dialog', (d) => d.dismiss());
const logs = [];
pg.on('console', (m) => logs.push(m.text()));

let failures = 0;
function check(name, cond, detail = '') {
  console.log((cond ? '  PASS ' : '  FAIL ') + name + (cond || !detail ? '' : '  -- ' + detail));
  if (!cond) failures++;
}
const settle = () => pg.waitForTimeout(1000);
const adds = () => requests.filter((r) => r.url.startsWith('/cart/add'));
const ids = () => adds().map((r) => r.fields.id).join(',');
const qtyOf = (v) => cart.filter((l) => l.variant_id === v).reduce((n, l) => n + l.quantity, 0);
async function fillPack(n, name, bday) {
  await pg.fill('#tda-pm-name-' + n, name);
  await pg.fill('#tda-pm-bday-' + n, bday);
}
const open = () => pg.goto(base + '/products/the-birth-day-archive-pack');

console.log('\nScenario 1 - one archive: $20 card included');
resetCart(); await open();
check('reward row reads $20 / Included', (await pg.textContent('#tda-pm-reward-title')).includes('$20') && (await pg.textContent('#tda-pm-reward-state')) === 'Included');
check('badge offers the $25 upgrade', (await pg.textContent('#tda-pm-badge')).includes('$25 GIFT CARD'));
await pg.click('#atc'); await settle();
check('2 adds: archive then $20 card', ids() === ARCHIVE + ',' + GC20, ids());
check('card carries _Bonus', adds()[1] && adds()[1].fields['properties[_Bonus]'] === 'Free $20 Gift Card - 1 Archive');
check('exactly one card in cart', qtyOf(GC20) === 1 && qtyOf(GC25) === 0);
check('guard leaves it alone', !requests.some((r) => r.url === '/cart/change.js'));
check('Kaching got 200', (await pg.evaluate(() => window.__lastStatus)) === 200);

console.log('\nScenario 2 - one archive + frame: one card, one frame');
resetCart(); await open();
await pg.check('#tdaFrameCheckbox');
await pg.click('#atc'); await settle();
check('archive, frame and $20 card all added', qtyOf(ARCHIVE) === 1 && qtyOf(FRAME) === 1 && qtyOf(GC20) === 1, ids());
check('no $25 card', qtyOf(GC25) === 0);
check('only one gift card request', adds().filter((r) => r.fields.id === String(GC20)).length === 1, ids());

console.log('\nScenario 3 - two archives: upgraded to $25');
resetCart(); await open();
await pg.click('#tda-pm-add-btn');
check('reward row swaps to $25 / Upgraded', (await pg.textContent('#tda-pm-reward-title')).includes('$25') && (await pg.textContent('#tda-pm-reward-state')) === 'Upgraded');
check('badge hidden once added', await pg.$eval('#tda-pm-badge', (e) => e.style.display === 'none'));
await fillPack(2, 'Tom Stafford', '02/11/1968');
await pg.click('#atc'); await settle();
check('3 adds: archive, archive, $25 card', ids() === ARCHIVE + ',' + ARCHIVE + ',' + GC25, ids());
check('pack 2 personalisation kept', adds()[1].fields['properties[Full Name]'] === 'Tom Stafford' && adds()[1].fields['properties[_Pack]'] === '2 of 2');
check('no $20 card', qtyOf(GC20) === 0 && qtyOf(GC25) === 1);

console.log('\nScenario 4 - three archives + two frames');
resetCart(); await open();
await pg.click('#tda-pm-add-btn'); await pg.click('#tda-pm-add-btn');
await fillPack(2, 'Tom Stafford', '02/11/1968');
await fillPack(3, 'Ella Stafford', '30/07/1994');
await pg.check('#tdaFrameCheckbox');
await pg.waitForSelector('#tda-fq2', { state: 'attached' });
await pg.check('#tda-fq2');
await pg.click('#atc'); await settle();
check('order: 3 archives, $25 card, frames', ids() === [ARCHIVE, ARCHIVE, ARCHIVE, GC25, FRAME].join(','), ids());
check('frame quantity 2', qtyOf(FRAME) === 2);
check('one $25 card', qtyOf(GC25) === 1);

console.log('\nScenario 5 - empty 2nd pack blocks everything');
resetCart(); await open();
await pg.click('#tda-pm-add-btn');
await pg.click('#atc'); await settle();
check('nothing reached the cart', requests.length === 0, JSON.stringify(requests));
check('422 returned', (await pg.evaluate(() => window.__lastStatus)) === 422);

console.log('\nScenario 6 - guard downgrades $25 to $20 when an archive is removed');
resetCart(); await open();
await pg.click('#tda-pm-add-btn');
await fillPack(2, 'Tom Stafford', '02/11/1968');
await pg.click('#atc'); await settle();
check('setup: 2 archives + $25 card', qtyOf(ARCHIVE) === 2 && qtyOf(GC25) === 1);
const archiveKey = cart.find((l) => l.variant_id === ARCHIVE).key;
await pg.evaluate((key) => fetch('/cart/change.js', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: key, quantity: 0 }) }), archiveKey);
await pg.waitForTimeout(2500);
check('$25 card gone', qtyOf(GC25) === 0, JSON.stringify(cart));
check('$20 card in its place', qtyOf(GC20) === 1, JSON.stringify(cart));
check('one archive remains', qtyOf(ARCHIVE) === 1);

console.log('\nScenario 7 - guard removes the card when the last archive goes');
resetCart(); await open();
await pg.click('#atc'); await settle();
const lastArchive = cart.find((l) => l.variant_id === ARCHIVE).key;
await pg.evaluate((key) => fetch('/cart/change.js', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ id: key, quantity: 0 }) }), lastArchive);
await pg.waitForTimeout(2500);
check('no bonus card left', qtyOf(GC20) === 0 && qtyOf(GC25) === 0, JSON.stringify(cart));

console.log('\nScenario 8 - a gift card the shopper bought is never touched');
resetCart();
addLine({ id: String(GC20), quantity: '1' });
addLine({ id: String(ARCHIVE), quantity: '1', 'properties[Full Name]': 'A', 'properties[Birthday]': '01/01/1970' });
await open(); await settle();
check('purchased card still there', qtyOf(GC20) === 1);
check('guard made no changes', !requests.some((r) => r.url === '/cart/change.js'));

console.log('\nScenario 9 - gift card add failing does not break the order');
resetCart(); rejectGift = true; await open();
await pg.click('#tda-pm-add-btn');
await fillPack(2, 'Tom Stafford', '02/11/1968');
await pg.click('#atc'); await settle();
check('both archives still added', qtyOf(ARCHIVE) === 2);
check('Kaching still got 200', (await pg.evaluate(() => window.__lastStatus)) === 200);
check('failure logged', logs.some((l) => l.includes('Gift card add failed')));

await browser.close();
server.close();
console.log(failures === 0 ? '\nALL PASSED' : '\n' + failures + ' FAILED');
process.exit(failures === 0 ? 0 : 1);
