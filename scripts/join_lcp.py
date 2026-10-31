#!/usr/bin/env python3
from pathlib import Path
a = Path('scripts/lcp_part_a.tsx').read_text()
b = Path('scripts/lcp_part_b.tsx').read_text()
Path('src/components/LiveChatPage.tsx').write_text(a + b)
print('joined', len(a) + len(b))
