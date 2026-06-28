from __future__ import annotations

import re
import socketserver
import subprocess
import threading
import urllib.request
from functools import partial
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = [ROOT / 'index.html', ROOT / 'chile.html']


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, fmt: str, *args):
        return


def compile_inline_scripts(path: Path) -> None:
    text = path.read_text(encoding='utf-8', errors='replace')
    blocks = re.findall(r'<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>', text, flags=re.I | re.S)
    for i, block in enumerate(blocks, 1):
        if not block.strip():
            continue
        tmp = ROOT / f'.__smoke_{path.stem}_{i}.js'
        tmp.write_text(block, encoding='utf-8')
        try:
            proc = subprocess.run(['node', '--check', str(tmp)], text=True, capture_output=True, timeout=30)
            if proc.returncode != 0:
                raise SystemExit(f'NODE_CHECK FAIL {path.name} script#{i}\n{(proc.stdout + proc.stderr)[-1200:]}')
            print(f'NODE_CHECK {path.name} script#{i}: OK')
        finally:
            tmp.unlink(missing_ok=True)


def assert_structure(path: Path) -> None:
    text = path.read_text(encoding='utf-8', errors='replace')
    refs = re.findall(r'(?:src|href)=["\']([^"\']+)["\']', text, flags=re.I)
    missing = []
    for ref in refs:
        if ref.startswith(('http://', 'https://', '#', 'mailto:', 'tel:', 'data:', '//')):
            continue
        candidate = (ROOT / ref.split('?', 1)[0].split('#', 1)[0]).resolve()
        if not candidate.exists():
            missing.append(ref)
    if missing:
        raise SystemExit(f'MISSING_ASSETS {path.name}: ' + ', '.join(missing[:20]))

    required_markers = [
        'query1.finance.yahoo.com/v8/finance/chart',
        'chart?.result?.[0]?.meta',
        'regularMarketPrice',
    ]
    for marker in required_markers:
        if marker not in text:
            raise SystemExit(f'{path.name} perdió marcador crítico de Yahoo: {marker}')

    if path.name == 'index.html':
        for marker in ['id="portfolio-table"', 'id="chartHistory"', 'id="chartDonut"', 'id="chartCost"', 'const portfolio = [', 'const recommendations = [']:
            if marker not in text:
                raise SystemExit(f'index.html sin marcador esperado: {marker}')
        positions = len(re.findall(r'\{\s*ticker:"', text))
        if positions < 10:
            raise SystemExit(f'index.html parece vacío: solo {positions} posiciones detectadas')
    else:
        for marker in ['id="portfolio-table"', 'id="chartHistoryCLP"', 'id="chartDonut"', 'id="chartCost"', 'const portfolio = [']:
            if marker not in text:
                raise SystemExit(f'chile.html sin marcador esperado: {marker}')
        positions = len(re.findall(r'\{\s*ticker:"', text))
        if positions < 5:
            raise SystemExit(f'chile.html parece vacío: solo {positions} posiciones detectadas')
    print(f'STRUCTURE {path.name}: posiciones={positions}')


def serve_and_fetch() -> None:
    handler = partial(QuietHandler, directory=str(ROOT))
    with socketserver.TCPServer(('127.0.0.1', 0), handler) as httpd:
        port = int(httpd.server_address[1])
        thread = threading.Thread(target=httpd.serve_forever, daemon=True)
        thread.start()
        try:
            for rel in ['/', '/index.html', '/chile.html']:
                with urllib.request.urlopen(f'http://127.0.0.1:{port}{rel}', timeout=5) as resp:
                    text = resp.read().decode('utf-8', errors='replace')
                    if resp.status != 200:
                        raise SystemExit(f'HTTP {resp.status} en {rel}')
                    if 'Cargando precios en vivo' not in text and 'Portfolio' not in text:
                        raise SystemExit(f'Respuesta inesperada en {rel}')
                    print(f'HTTP {rel}: OK')
        finally:
            httpd.shutdown()
            thread.join(timeout=5)


def main() -> None:
    for html in HTML_FILES:
        assert_structure(html)
        compile_inline_scripts(html)
    serve_and_fetch()


if __name__ == '__main__':
    main()
