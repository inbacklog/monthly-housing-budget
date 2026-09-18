"""Create a self-contained Homeflow HTML file. Standard-library Python only.
No build is required for GitHub Pages; this helper creates an optional local copy.
Usage: python tools/build_offline.py [output.html]
"""
from pathlib import Path
import base64
import mimetypes
import sys

BASE = Path(__file__).resolve().parents[1]
VERSION = '1.1.1'

def data_uri(relative: str) -> str:
    path = BASE / relative
    mime = mimetypes.guess_type(path.name)[0] or 'application/octet-stream'
    return 'data:' + mime + ';base64,' + base64.b64encode(path.read_bytes()).decode('ascii')

def build() -> str:
    html = (BASE / 'index.html').read_text(encoding='utf-8')
    html = html.replace('<link rel="stylesheet" href="styles.css">', '<style>\n' + (BASE / 'styles.css').read_text(encoding='utf-8') + '\n</style>')
    html = html.replace('<link rel="manifest" href="manifest.webmanifest">', '')
    scripts = []
    for filename in ['engine.js', 'presets.js', 'app.js']:
        html = html.replace(f'<script src="{filename}" defer></script>', '')
        scripts.append((BASE / filename).read_text(encoding='utf-8').replace('</script', '<\\/script'))
    # Inline scripts ONLY at the end of the body, after all DOM targets exist.
    html = html.replace('</body>', '<script>window.HOMEFLOW_OFFLINE=true;</script>' + ''.join('<script>\n' + s + '\n</script>' for s in scripts) + '</body>')
    for asset in ['assets/icon.svg', 'assets/icon-192.png', 'assets/buymeacoffee-qr.png', 'assets/wallet-of-satoshi-qr.png', 'templates/Household_Budget_Import_Template.xlsx']:
        html = html.replace(asset, data_uri(asset))
    return html

if __name__ == '__main__':
    destination = Path(sys.argv[1]) if len(sys.argv) > 1 else BASE.parent / f'Homeflow_Offline_v{VERSION}.html'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(build(), encoding='utf-8')
    print(destination)
