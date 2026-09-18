"""Verify the support images are exact copies, not regenerated QR codes."""
from pathlib import Path
from hashlib import sha256
import importlib.util,re,base64
BASE=Path(__file__).resolve().parents[1]
EXPECTED={'wallet-of-satoshi-qr.png': '05552b6a33f4978e659a695cad12c104cb313055ff2370fc35b975263469d060', 'buymeacoffee-qr.png': '8b07e2b1470b5426e50ddac4f7497591bcaf74ec728231f0b5b2c6aef316e58c'}
for name,expected in EXPECTED.items():
    assert sha256((BASE/'assets'/name).read_bytes()).hexdigest()==expected,name
    print('PASS original PNG bytes:',name)
spec=importlib.util.spec_from_file_location('builder',BASE/'tools/build_offline.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
html=m.build()
images=[base64.b64decode(x) for x in re.findall(r'<img[^>]+src="data:image/png;base64,([^"]+)"',html)]
for name in EXPECTED:
    assert (BASE/'assets'/name).read_bytes() in images,name
    print('PASS standalone embeds original bytes:',name)
assert 'homeflow-static-v1.3.0' in (BASE/'sw.js').read_text()
print('PASS new asset cache version')
print('5 QR-asset checks passed.')
