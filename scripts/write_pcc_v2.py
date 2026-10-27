#!/usr/bin/env python3
from pathlib import Path
parts = [Path(f"scripts/pcc_p{i}.txt").read_text() for i in range(8)]
Path("src/components/PortalCommunityChat.tsx").write_text("".join(parts))
print("written", Path("src/components/PortalCommunityChat.tsx").stat().st_size)
