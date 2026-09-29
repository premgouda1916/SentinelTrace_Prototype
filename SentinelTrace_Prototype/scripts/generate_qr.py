import sys
from pathlib import Path
import qrcode

if len(sys.argv) != 2 or not sys.argv[1].startswith(('http://','https://')):
    raise SystemExit('Usage: python scripts/generate_qr.py https://your-public-demo-url')
url=sys.argv[1]
out=Path(__file__).resolve().parents[1]/'qr_code.png'
img=qrcode.make(url)
img.save(out)
print(f'QR written to {out}')
print(f'LIVE_DEMO_URL={url}')
