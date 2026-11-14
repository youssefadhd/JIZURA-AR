"""Browser tests for Arabic shaping, bidi, language selection and existing scripts.

Run after ``python build.py --dev`` with ``python dev/arabic_test.py``.
Requires the same Python Playwright setup as smoke_all.py.
"""
import asyncio
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os
from pathlib import Path
import sys
import threading

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / 'dev' / 'www'
CASES = [
    ('Arabic', 'مرحباً بالعالم', 'ar'),
    ('Arabic with diacritics', 'السَّلَامُ عَلَيْكُمْ', 'ar'),
    ('Mixed Arabic and English', 'مرحباً Joey 2026', 'ar'),
    ('Arabic punctuation', 'مرحبًا، كيف حالك؟ (2026)!', 'ar'),
    ('English', 'Hello World.', 'en'),
    ('Japanese', 'こんにちは世界。', 'ja'),
]


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *_args):
        pass


async def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    if not (WEB / 'test.html').exists() or not (WEB / 'jizura.js').exists():
        raise SystemExit('Missing dev/www bundle; run python build.py --dev first')
    os.chdir(ROOT)
    server = ThreadingHTTPServer(('127.0.0.1', 0), QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    failures = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            page.on('pageerror', lambda error: failures.append(f'Browser error: {error}'))
            base = f'http://127.0.0.1:{server.server_port}'
            await page.goto(base + '/dev/www/test.html')
            await page.add_script_tag(url=base + '/vendor/mp4-muxer.min.js')
            result = await page.evaluate("""async cases => {
              const checks = [];
              const assert = (ok, msg) => { if (!ok) throw new Error(msg); };
              for (const [name, text, lang] of cases) {
                const detected = J.detectLang(text);
                const useLang = lang === 'ar' ? 'ar' : lang;
                J.setLang(useLang);
                const font = J.faceOf('gothic_med');
                if (lang === 'ar') await J.ensureFonts(text, ['gothic_med']);
                const item = { text, font: 'gothic_med', size: 80, x: 240, y: 110, align: 'center', color: '#fff' };
                const layout = J.layoutText(item);
                const c = document.createElement('canvas'); c.width = 480; c.height = 220;
                const ctx = c.getContext('2d');
                const seen = [];
                const fill = ctx.fillText.bind(ctx);
                ctx.fillText = (s, ...args) => { seen.push({ text: s, direction: ctx.direction }); return fill(s, ...args); };
                const bounds = J.drawItem({ ctx, pass: 'main', scale: 1, allowFilter: false }, item);
                const pixels = ctx.getImageData(0, 0, c.width, c.height).data;
                let ink = 0; for (let i = 3; i < pixels.length; i += 4) if (pixels[i] > 0) ink++;
                assert(bounds && ink > 20, name + ': expected visible rendered text');
                if (lang === 'ar') {
                  assert(detected === 'ar', name + ': detected as ' + detected);
                  assert(layout.length === 1 && layout[0].ch === text, name + ': Arabic line must remain one intact shaped run');
                  const verticalLayout = J.layoutText(Object.assign({}, item, { vertical: true }));
                  assert(verticalLayout.length === 1 && verticalLayout[0].ch === text, name + ': Arabic must remain horizontal and shaped in vertical layouts');
                  assert(seen.some(x => x.text === text && x.direction === 'rtl'), name + ': expected original text drawn with RTL direction');
                  assert(font.family.includes('Noto Sans Arabic'), name + ': expected Noto Sans Arabic font face, got ' + font.family);
                  assert(J.faceOf('mincho').family.includes('Noto Naskh Arabic'), name + ': expected Noto Naskh Arabic serif face');
                  assert(J.chunkText(text).length === 1, name + ': planner must keep Arabic line together');
                } else {
                  assert(detected === lang, name + ': detected as ' + detected);
                  assert(layout.length === [...text].length, name + ': legacy per-character layout changed');
                  assert(seen.map(x => x.text).join('') === text.replace(/\s/g, ''), name + ': legacy characters were not drawn in source order');
                }
                checks.push(name + ': PASS (detected=' + detected + ', groups=' + layout.length + ', ink=' + ink + ')');
              }
              const project = Object.assign(J.defaultProject(), { lyrics: cases[0][1], lang: 'ar', aspect: '16:9', res: 720, fps: 24, style: 'noir', seed: 2718 });
              const plan = J.plan(project, null);
              await J.ensureFonts(project.lyrics, J.fontsOfPlan(plan));
              const preview = document.createElement('canvas'); preview.width = 640; preview.height = 360;
              const renderer = new J.Renderer();
              renderer.frame(preview.getContext('2d'), plan, 0.5, { scale: 0.5, fast: true });
              const previewPixels = preview.getContext('2d').getImageData(0, 0, preview.width, preview.height).data;
              assert(previewPixels.some((v, i) => i % 4 === 3 && v > 0), 'Animated preview frame is empty');
              checks.push('Renderer frame (preview / animation): PASS (plan.lang=' + plan.lang + ')');
              const png = await J.exportPNGZip({ plan, project, every: Math.max(1, Math.ceil(plan.duration * plan.fps)) });
              assert(png.size > 1000, 'PNG ZIP export is unexpectedly small');
              checks.push('PNG frame export: PASS (' + png.size + ' bytes)');
              try {
                const mp4 = await J.exportMP4({ plan, project, audio: null, quality: 'standard' });
                assert(mp4.blob && mp4.blob.size > 1000, 'MP4 export is unexpectedly small');
                checks.push('MP4 export: PASS (' + mp4.size + ' bytes, ' + mp4.codec + ')');
              } catch (e) {
                checks.push('MP4 export: FAIL (' + (e && e.message || e) + ')');
              }
              return checks;
            }""", CASES)
            for check in result:
                print(check)
            failed_checks = [check for check in result if ': FAIL' in check]
            if failed_checks:
                raise RuntimeError('\n'.join(failed_checks))
            if failures:
                raise RuntimeError('\n'.join(failures))
            await browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
