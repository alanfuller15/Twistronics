// v31 3D refresh audit: WebGL (swiftshader) and forced Canvas fallback; desktop/mobile/200% text.
const { chromium } = require('playwright');
const out = process.argv[2], BASE = 'http://127.0.0.1:8776/';
(async () => {
  const results = [];
  for (const mode of ['webgl', 'canvas']) {
    const args = mode === 'webgl' ? ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] : ['--disable-webgl', '--disable-webgl2', '--disable-3d-apis'];
    const b = await chromium.launch({ args });
    for (const [w, zoom] of [[1280, 1], [390, 1], [390, 2]]) {
      for (const page_ of ['index.html', 'graphene.html']) {
        const ctx = await b.newContext({ viewport: { width: w, height: 900 } }); const p = await ctx.newPage();
        const errs = [], fails = [];
        p.on('pageerror', e => errs.push('pageerror: ' + e.message)); p.on('console', m => { if (m.type() === 'error') errs.push(m.text()); });
        p.on('response', r => { if (r.status() >= 400) fails.push(r.url() + ' ' + r.status()); });
        const routes = page_ === 'index.html' ? ['#bands', '#wave', '#graphene'] : [''];
        const acts = [];
        const settle = async id => (await p.evaluate(i => (document.getElementById(i) || {}).textContent || '', id)).trim().slice(0, 60);
        const shot = async (sel, path) => { try { await p.locator(sel).screenshot({ path, timeout: 8000 }); } catch (e) { acts.push('screenshot ' + sel + ':FAIL'); } };
        const act = async (label, fn) => { try { await fn(); acts.push(label + ':ok'); } catch (e) { acts.push(label + ':FAIL ' + String(e.message).slice(0, 80)); } };
        const settle0 = async id => { const t0 = Date.now(); while (Date.now() - t0 < 25000) { const t = await p.evaluate(i => (document.getElementById(i) || {}).textContent || '', id); if (!/Preparing|Loading/.test(t)) return t.trim().slice(0, 90); await p.waitForTimeout(250); } return 'STILL: ' + (await p.evaluate(i => document.getElementById(i).textContent, id)).trim().slice(0, 60); };
        for (const route of routes) {
          await p.goto(BASE + page_ + route); await p.waitForTimeout(6000); await p.evaluate(r => { const root = r ? document.querySelector(r) : document; root.querySelectorAll('details').forEach(d => d.open = true); }, route); await p.waitForTimeout(500);
          if (zoom !== 1) await p.addStyleTag({ content: `html{font-size:${zoom * 100}% !important}` });
          if (route === '#bands') {
            acts.push('band-status=' + await settle('band-render-status'));
            for (const id of ['band-top', 'band-rotate-left', 'band-tilt-up', 'band-zoom-in', 'band-reset']) await act(id, async () => { await p.click('#' + id, { timeout: 5000 }); await p.waitForTimeout(250); });
            await act('band-select-marker', async () => { const bb = await p.locator('#band-canvas').boundingBox(); await p.mouse.click(bb.x + bb.width / 2, bb.y + bb.height / 2); await p.waitForTimeout(300); });
            await shot('#band-canvas', `${out}/${mode}-${w}-z${zoom}-bands.png`);
          }
          if (route === '#wave') {
            acts.push('wave-status=' + await settle('wave-status'));
            for (const v of ['density', 'amplitude']) {
              await act('wave-height=' + v, async () => { await p.selectOption('#wave-height', v, { timeout: 5000 }); await p.waitForTimeout(500); });
              await shot('#wave-position', `${out}/${mode}-${w}-z${zoom}-wave-${v}.png`);
            }
            await act('wave-camera', async () => { await p.locator('[data-wave-camera="left"]').first().click({ timeout: 5000 }); await p.locator('[data-wave-camera="reset"]').first().click({ timeout: 5000 }); });
            await act('wave-play', async () => { await p.locator('[data-wave-play]').first().click({ timeout: 5000 }); await p.waitForTimeout(800); await p.locator('[data-wave-play]').first().click(); });
            await shot('#wave-momentum', `${out}/${mode}-${w}-z${zoom}-wave-momentum.png`);
          }
          if (route === '#graphene' || page_ === 'graphene.html') {
            acts.push('graphene-status=' + await settle('graphene-status'));
            await act('graphene-play', async () => { await p.click('#graphene-play', { timeout: 5000 }); await p.waitForTimeout(1200); await p.click('#graphene-play'); });
            await act('graphene-scrub', async () => { await p.evaluate(() => { const s = document.getElementById('graphene-scrub'); s.value = String(Math.round((+s.min + +s.max) / 2)); s.dispatchEvent(new Event('input', { bubbles: true })); s.dispatchEvent(new Event('change', { bubbles: true })); }); await p.waitForTimeout(500); });
            await shot('#graphene-canvas', `${out}/${mode}-${w}-z${zoom}-${page_.replace('.html', '')}-graphene.png`);
          }
        }
        const info = await p.evaluate(() => ({
          scrollW: document.documentElement.scrollWidth, innerW: innerWidth,
          renderers: [...document.querySelectorAll('canvas')].map(c => (c.id || '?') + '=' + (c.dataset.renderer || '-')),
          overflow: [...document.querySelectorAll('body *')].filter(e => { const r = e.getBoundingClientRect(); return r.width > 0 && r.right > innerWidth + 1 && getComputedStyle(e).position !== 'fixed' && !e.closest('.table-wrap,.candidate-table-wrap'); }).slice(0, 4).map(e => e.tagName + '#' + e.id + '.' + e.className),
          status: ['band-render-status', 'graphene-status', 'wave-status'].map(id => { const e = document.getElementById(id); return e ? id + ': ' + e.textContent.trim().slice(0, 90) : null; }).filter(Boolean),
        }));
        results.push({ mode, w, zoom, page: page_, info, acts, errs: errs.slice(0, 5), fails });
        console.log(JSON.stringify(results.at(-1)));
        await ctx.close();
      }
    }
    await b.close();
  }
})();
