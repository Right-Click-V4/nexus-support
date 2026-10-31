#!/usr/bin/env python3
import base64
from pathlib import Path
parts = []
parts.append(Path('scripts/lcp_emoji_b64_0.txt').read_text().strip())
parts.append(Path('scripts/lcp_emoji_b64_1.txt').read_text().strip())
parts.append(Path('scripts/lcp_emoji_b64_2.txt').read_text().strip())
parts.append(Path('scripts/lcp_emoji_b64_3.txt').read_text().strip())
parts.append(Path('scripts/lcp_emoji_b64_4.txt').read_text().strip())
raw = base64.b64decode(''.join(parts).encode()).decode()
Path('src/components/LiveChatPage.tsx').write_text(raw)
print('wrote LiveChatPage', len(raw))
