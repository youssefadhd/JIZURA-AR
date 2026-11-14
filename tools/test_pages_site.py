"""Smoke-test the GitHub Pages artifact under a project subpath.

Usage after ``python build.py --out-dir site --base-url URL --english-root``:
    python tools/test_pages_site.py

Requires Python Playwright and its Chromium browser, as used by dev/smoke_all.py.
"""
import asyncio
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys
import threading
from urllib.parse import urlsplit

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / 'site'
PREFIX = '/JIZURA-AR/'
SITE_BASE = os.environ.get('JIZURA_SITE_BASE', 'https://example.github.io/JIZURA-AR/').rstrip('/') + '/'
PAGES = [
    ('', 'en'), ('ja/', 'ja'), ('zh-hant/', 'zh-Hant'), ('zh-hans/', 'zh-Hans'),
    ('ko/', 'ko'), ('id/', 'id-ID'), ('vi/', 'vi'),
]


class PrefixHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(SITE), **kwargs)

    def translate_path(self, path):
        pathname = urlsplit(path).path
        if pathname == PREFIX.rstrip('/'):
            pathname = PREFIX
        if pathname.startswith(PREFIX):
            pathname = '/' + pathname[len(PREFIX):]
        return super().translate_path(pathname)

    def log_message(self, *_args):
        pass


async def main():
    if not (SITE / 'index.html').is_file():
        raise SystemExit('Missing site/index.html; build the production site first')
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    server = ThreadingHTTPServer(('127.0.0.1', 0), PrefixHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    errors = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            page.on('pageerror', lambda error: errors.append(str(error)))
            base = f'http://127.0.0.1:{server.server_port}{PREFIX}'
            for route, lang in PAGES:
                response = await page.goto(base + route, wait_until='load')
                if response is None or response.status != 200:
                    raise AssertionError(f'{route or "root"}: HTTP {response.status if response else "no response"}')
                got = await page.locator('html').get_attribute('lang')
                if got != lang:
                    raise AssertionError(f'{route or "root"}: expected html lang {lang}, got {got}')
                result = await page.evaluate("""() => {
                  const nav = document.querySelector('.lang-switch select');
                  const paths = nav ? [...nav.options].map(o => new URL(o.value, location.href).pathname) : [];
                  return {
                    title: document.title,
                    canonical: document.querySelector('link[rel=canonical]')?.href,
                    paths,
                    externalAssets: [...document.querySelectorAll('script[src], link[rel=stylesheet], img[src]')].filter(el => el.tagName !== 'LINK' || new URL(el.href).hostname !== 'fonts.googleapis.com').length,
                    arabicOption: !!document.querySelector('#lyricLang option[value=ar]'),
                    muxer: typeof Mp4Muxer !== 'undefined' && !!Mp4Muxer.Muxer,
                    arabicDetection: J.detectLang('مرحباً Joey 2026'),
                    arabicLayout: (() => { J.setLang('ar'); const g=J.layoutText({text:'السَّلَامُ عَلَيْكُمْ',font:'gothic_med',size:80}); return g.length===1 && g[0].dir==='rtl' && g[0].ch==='السَّلَامُ عَلَيْكُمْ'; })(),
                  };
                }""")
                expected = {'index.html', 'ja/index.html', 'zh-hant/index.html', 'zh-hans/index.html', 'ko/index.html', 'id/index.html', 'vi/index.html'}
                under = [path.split('/JIZURA-AR/', 1)[-1] for path in result['paths']]
                if set(under) != expected:
                    raise AssertionError(f'{route or "root"}: language links escape the subpath or omit an edition: {under}')
                checks = {
                    'canonical stays under project base': result['canonical'].startswith(SITE_BASE),
                    'no missing external asset files': result['externalAssets'] == 0,
                    'Arabic selector present': result['arabicOption'],
                    'MP4 muxer bundled': result['muxer'],
                    'Arabic auto-detection': result['arabicDetection'] == 'ar',
                    'Arabic shaped RTL line': result['arabicLayout'],
                }
                failed = [name for name, ok in checks.items() if not ok]
                if failed:
                    raise AssertionError(f'{route or "root"}: ' + ', '.join(failed))
                print(f'{route or "root"}: PASS ({lang}, {len(under)} relative edition links)')
            if errors:
                raise AssertionError('Browser errors: ' + '; '.join(errors))
            await browser.close()
    finally:
        server.shutdown()


if __name__ == '__main__':
    asyncio.run(main())
