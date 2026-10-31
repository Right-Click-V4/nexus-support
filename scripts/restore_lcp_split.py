#!/usr/bin/env python3
import zlib, base64
from pathlib import Path
c = Path('scripts/lcp_z0.txt').read_text().strip() + Path('scripts/lcp_z1.txt').read_text().strip()
raw = zlib.decompress(base64.b64decode(c)).decode()
Path('src/components/LiveChatPage.tsx').write_text(raw)
print('restored', len(raw))
